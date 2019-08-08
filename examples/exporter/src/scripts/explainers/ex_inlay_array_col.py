# -*- coding: utf-8 -*-
#

"""
将表格中一列中的内容，解释为一个元组列表（二维数组）
其中元组的元素个数固定

如：
  key     tuple          list
|-----|---------------------------|
|  1  | (11, 22)(33, 44)          |    导出为 [(11, 22), (33, 44), ]
|-----|---------------------------|
|  2  | (22, 44),(66, 88)(10, 10) |    导出为 [(22, 44), (66, 88), (10, 10), ]
|-----|---------------------------|
|  3  | 55, 66                    |    导出为 [(55, 66), ]
|-----|---------------------------|
|  4  | 77                        |    导出为 [(77, 0), ] 即元素的第二个值为类型默认值
|-----|---------------------------|


writen by yongwei-huang -- 2013.04.12
"""

import re
import utils
from define import ABANDON_COL
from config.CustomConfig import CustomConfig
from ExplainExceptions import ExplainErrorValueTypeException
from ex_base import ex_base
from ex_base import ex_col_base

class ex_list_tuple_col(ex_col_base):
	"""
	extras 中除了 ex_base 中指定的参数，还可以增加以下参数：
		arrSplitters: 指定一组元素之间的分隔符号，如果不指定，则默认使用 config.xml 配置中指定的符号作为分隔符
		tupleScopeStarts: 指定元组区间起始符
		tupleScopeEnds: 指定元组区间结束符

	etypes 为元素列表列表
	如：
		(int, float) 导出结果为：[(int, float), ....]
		(hlint, bool, xfloat[2]) 导出结果为：[(hlint, bool, xfloat[2]), ....]
	"""
	def __init__(self, key, etypes, defValue=ex_base.INNER, **extras):
		assert len(etypes) > 1, "the number of element must large than 1."
		ex_col_base.__init__(self, key, defValue, **extras)
		self.__etypes = etypes
		self.splitters_ = self.query("arrSplitters", (str,))				# 元组分隔符，可以被子类对象修改
		self.__tupleScopeStarts = self.query("tupleScopeStarts", (str, ))	# 元组区间起始符，可以被子类对象修改
		self.__tupleScopeEnds = self.query("tupleScopeEnds", (str, ))		# 元组区间结束符，可以被子类对象修改


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __explain1(self, dsrc, row, text):
		try:
			elems = [self.__etypes[0](text)]
			for etype in self.__etypes[1:]:
				elems.append(etype())
			return [tuple(elems)]
		except ValueError:
			raise ExplainErrorValueTypeException(dsrc, row, self.key)

	def __explain2(self, dsrc, row, text):
		elems = []
		strElems = utils.splits(text, self.splitters_)
		count = len(strElems)
		try:
			for idx, etype in enumerate(self.__etypes):
				if idx < count:
					strElem = strElems[idx].strip()
					if strElem == "":
						elems.append(etype())
					else:
						elems.append(etype(strElem))
				else:
					elems.append(etype())
		except ValueError:
			raise ExplainErrorValueTypeException(dsrc, row, self.key)
		return[tuple(elems)]

	def __explain3(self, dsrc, row, text):
		elems = []
		for strElem in utils.findScopes(text, self.__tupleScopeStarts, self.__tupleScopeEnds):
			elems.extend(self.__explain2(dsrc, row, strElem))
		return elems


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def filter_(self, dsrc, row, value=ex_base.INNER):
		"""
		如果构造函数中传入 extra 的参数带有 excludeValue 则：
			1、如果解释内容为空，则返回 ABANDON_COL
			2、如果解释内容与 exclueValue 值相等，则返回 ABANDON_COL
		如果构造函数中传入的 extra 参数中没带有 excludeValue 则：
			1、如果解释内容为空，同时传入了 defValue，则返回 defValue
			2、如果解释内容为空，但没传入 defValue，则返回 tuple 或 list 对象
		"""
		if value is ex_base.INNER:											# 解释内容为空
			if self.isExcludeValue_():										# 有排除值
				return ABANDON_COL
			elif self.defValue_ is ex_base.INNER:							# 没有传入默认值
				return self.fnRet([])
			return self.fnRet(self.defValue_)
		elif self.isExcludeValue_(value):									# 解释内容与排除值相等
			return ABANDON_COL
		elif value is ex_base.ERR_TYPE:										# 解释内容类型不正确
			raise ExplainErrorValueTypeException(dsrc, row, self.key)
		return self.fnRet(value)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __call__(self, dsrc, row):
		text = self.getCellText_(dsrc, row)
		if text == "":													# 没有任何内容
			return self.filter_(dsrc, row)
		values = []
		if not utils.contains(text, self.splitters_):					# 元素只有一个值
			values = self.__explain1(dsrc, row, text)
		elif not utils.startsWiths(text, self.__tupleScopeStarts):		# 只有一组值
			values = self.__explain2(dsrc, row, text)
		else:
			values = self.__explain3(dsrc, row, text)
		return self.filter_(dsrc, row, values)
