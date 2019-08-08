# -*- coding: utf-8 -*-
#

"""
扫描数据源

2018.03.07: writen by hyw
"""

from define import KEYRET_NORMAL
from define import KEYRET_EMPTY
from define import KEYRET_IGNOR
from define import ABANDON_COL
from libs.custom_types.OrderDict import OrderDict
from explainers.ex_base import ex_base
from exporter.ExportExceptions import ExportFixException
from exporter.Scanner import Scanner
from TarsWidget import TarsAttrTag, _TarsAttrTag
from TarsWidget import TarsListValue, _TarsListValue


# --------------------------------------------------------------------
# 导出解释器，对应每一个 data_srcs/DataSource::iDataSource 的子类
# --------------------------------------------------------------------
class TarsScanner(Scanner):
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

	def __scanArray(self, dsrc, exp, row):
		"""
		解释一个列表
		"""
		elems = []
		for eExp in exp:
			elems.append(self.__scanValue(dsrc, eExp, row))
		return elems

	def __scanTarsListValue(self, dsrc, exp, row):
		"""
		解释一个 Tars 标签组
		"""
		tagName = exp.tagName
		values = self.__scanValue(dsrc, exp.values, row)
		if not iterable(values): values = [values]
		return _TarsListValue(tagName, values)

	def __scanValue(self, dsrc, eExp, row):
		"""
		获取表达式返回的数据
		"""
		vtype = type(eExp)
		if vtype is dict or vtype is OrderDict:
			value = self.__scanDict(dsrc, eExp, row)
		elif vtype in (tuple, list, set, frozenset):
			value = self.__scanArray(dsrc, eExp, row)
		elif isinstance(eExp, ex_base):
			value = eExp(dsrc, row)
		elif isinstance(eExp, TarsListValue):
			value = self.__scanTarsListValue(dsrc, eExp, row)
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
		elif isinstance(kExp, TarsAttrTag):
			keyName = kExp.keyExp(dsrc, row)
			if keyName in (KEYRET_IGNOR, KEYRET_EMPTY):
				return keyName
			attrs = {}
			for attrName, attrValue in kExp.attrs.iteritems():
				attrs[attrName] = self.__scanValue(dsrc, attrValue, row)
			key = _TarsAttrTag(keyName, **attrs)
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
		datas = dsrcTracer.datas											# 导出数据
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
		elif key in datas:													# 监听器不做任何操作，但键已经重复（有可能调用 onRowExplained 时修改了表，造成重复）
			count = dbKeys.get(key, 1)
			dbKeys[key] = count + 1
		else:																# 监听器不做任何操作
			datas[key] = value
