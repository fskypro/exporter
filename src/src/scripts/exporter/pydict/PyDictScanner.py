# -*- coding: utf-8 -*-
#

"""
扫描数据源

2011.09.20: writen by hyw
"""

from define import KEYRET_NORMAL
from define import KEYRET_EMPTY
from define import KEYRET_IGNOR
from define import ABANDON_COL
from libs.custom_types.OrderDict import OrderDict
from explainers.ex_base import ex_base
from ..ExportExceptions import ExportFixException
from ..Scanner import Scanner


# --------------------------------------------------------------------
# 导出解释器，对应每一个 data_srcs/DataSource::iDataSource 的子类
# --------------------------------------------------------------------
class PyDictScanner(Scanner):
	def __init__(self, outItemInfo):
		Scanner.__init__(self, outItemInfo)


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __scanDict(self, dsrc, exp, row):
		"""
		解释一个字典
		"""
		elems = OrderDict()
		for kExp, vExp in exp.iteritems():
			value = self.__scanValue(dsrc, vExp, row)
			if value is ABANDON_COL: continue				# 不导出该列
			key = self.__scanValue(dsrc, kExp, row)
			elems[key] = value
		return elems

	def __scanTuple(self, dsrc, exp, row):
		"""
		解释一个元组
		"""
		return tuple(self.__scanList(dsrc, exp, row))

	def __scanList(self, dsrc, exp, row):
		"""
		解释一个列表
		"""
		elems = []
		for eExp in exp:
			elems.append(self.__scanValue(dsrc, eExp, row))
		return elems

	def __scanSet(self, dsrc, exp, row):
		"""
		解释一个集合
		"""
		elems = set()
		for eExp in exp:
			elems.add(self.__scanValue(dsrc, eExp, row))
		return elems

	def __scanFrozenset(self, dsrc, exp, row):
		"""
		解释一个固定集合
		"""
		elems = set()
		for eExp in exp:
			elems.add(self.__scanValue(dsrc, eExp, row))
		return frozenset(elems)

	def __scanValue(self, dsrc, eExp, row):
		"""
		获取表达式返回的数据
		"""
		vtype = type(eExp)
		if vtype is dict or vtype is OrderDict:
			value = self.__scanDict(dsrc, eExp, row)
		elif vtype is tuple:
			value = self.__scanTuple(dsrc, eExp, row)
		elif vtype is list:
			value = self.__scanList(dsrc, eExp, row)
		elif vtype is set:
			value = self.__scanSet(dsrc, eExp, row)
		elif vtype is frozenset:
			value = self.__scanFrozenset(dsrc, eExp, row)
		elif isinstance(eExp, ex_base):
			value = eExp(dsrc, row)
		else:
			value = eExp
		return value

	# -------------------------------------------------
	def __scanMainKey(self, dsrc, kExp, row):
		"""
		解释导出表中的最外层主键
		"""
		if isinstance(kExp, ex_base):
			key = kExp(dsrc, row)
		elif type(kExp) is tuple:
			key = []
			for k in kExp:
				keyElem = self.__scanMainKey(dsrc, k, row)
				if keyElem in (KEYRET_IGNOR, KEYRET_EMPTY):
					return keyElem
				key.append(keyElem)
			key = tuple(key)
		else:
			raise ExportFixException("errFirstKey", cls="ex_base")
		return key

	def __scanMainValue(self, dsrc, eExp, row):
		"""
		解释导出表达式最外层键对应的值
		"""
		return self.__scanValue(dsrc, eExp, row)


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRowScaned_(self, dsrcTracer, exp, row):
		"""
		翻译导出表达式
		"""
		dsrc = dsrcTracer.dsrc
		datas = dsrcTracer.datas										# 导出数据
		dbKeys = dsrcTracer.dbKeys										# 重复的键
		ignorRows = dsrcTracer.ignorRows								# 忽略的行
		emptyRows = dsrcTracer.emptyRows								# 空行

		# 获取键
		kExp, vExp = exp.items()[0]
		key = self.__scanMainKey(dsrc, kExp, row)
		if key == KEYRET_IGNOR:											# 忽略该行
			ignorRows.append(row+1)
			return
		elif key == KEYRET_EMPTY:										# 该行为空行
			emptyRows.append(row+1)
			return

		# 获取值
		value = self.__scanMainValue(dsrc, vExp, row)
		ret = self.cbRowScanning(datas, key, value, row, dsrc)
		if ret == KEYRET_EMPTY:											# 监听器认为该行为空行，并提示
			emptyRows.append(row+1)
		elif ret == KEYRET_IGNOR:										# 监听器认为该行要忽略，并提示
			ignorRows.append(row+1)
		elif ret is KEYRET_NORMAL:										# 监听器认为忽略该行，并不需要提示
			return
		elif key in datas:												# 监听器不做任何操作，但键已经重复（有可能调用 onRowExplained 时修改了表，造成重复）
			count = dbKeys.get(key, 1)
			dbKeys[key] = count + 1
		else:															# 监听器不做任何操作
			datas[key] = value
