# -*- coding: utf-8 -*-
#

"""
将表格中一列中的内容，以指定分隔符隔开，并表达为一个列表（tuple 或 list）的解释器

如：
  key     tuple          list
|-----|-----------| ---------------|
|  1  | (11, 22)  |  [11, 22, 33]  |
|-----|-----------| ---------------|
|  2  | (22, 44)  |  [22, 44]      |
|-----|-----------| ---------------|


writen by yongwei-huang -- 2013.04.12
"""


import re
import utils
from define import ABANDON_COL
from config.CustomConfig import CustomConfig
from libs.custom_types.hlint import hlint
from libs.custom_types.xfloat import xfloat
from CustomTypes import StringTemplate
from ExplainExceptions import ExplainFixException
from ExplainExceptions import ExplainErrorValueTypeException
from ExplainExceptions import ExplainEnumValueException
from ex_base import ex_base
from ex_base import ex_col_base


# ------------------------------------------------------------------------------
# array col explainers
# extras 中除了 ex_base 中指定的参数，还可以增加以下参数：
#     arrSplitters: 指定一组元素之间的分隔符号，如果不指定，则默认使用 config.xml 配置中指定的符号作为分隔符
#     tupleScopeStarts: 指定元组区间起始符
#     tupleScopeEnds: 指定元组区间结束符
#     listScopeStarts: 指定列表区间起始符
#     listScopeEnds: 指定列表区间结束符
#     fillValues: 指定一个用于填充的值列表，当元素填写不够时，用 fillValues 中的元素对应填充
# 说明：
# 1、如果 ecount == 0，则：
#    1) 如果解释内容为空，并且传入了默认值 defValue，则返回 defValue
#    2）如果解释内容为空，但没有传入默认值 defValue 则：
#       如果 extras 字典参数中指定了 excludeValue，则会返回 ABANDON_COL
#       如果 extras 字典参数中没有指定 excludeValue，则返回空列表
# 2、如果 ecount > 0，则：
#    1）如果解释内容为空，并且传入了默认值 defValue，则返回 defValue
#    2）如果解释内容为空，但没有传入默认值 defValue 则：
#       如果 extras 字典参数中指定了 excludeValue，则会返回 ABANDON_COL
#       如果 extras 字典参数中没有指定 excludeValue，则会引起 ExplainErrorValueTypeException 异常
#    3）如果解释内容元素个数大于参数 ecount 参数值，则会返回内容中前 ecount 个元素
#    4）如果解释内容元素个数小于参数 ecount 参数值，则：
#       如果 extras 字典参数中指定了 fillValues，则用 fillValues 填充后面缺少的值
#       如果 extras 字典参数中没有 fillValues，则会抛出 ExplainErrorValueTypeException 异常
# 3、基于第 1 第 2 点解释出来的值 value：
#    如果 extras 字典参数中指定了 excludeValue == value，则会返回 ABANDON_COL
# ------------------------------------------------------------------------------
class ex_array_col_base(ex_col_base):
	def __init__(self, key, ecount, defValue=ex_base.INNER, **extras):
		ex_col_base.__init__(self, key, defValue, **extras)
		self.ecount_ = ecount
		self.fillValues_ = extras.get("fillValues", None)
		if self.fillValues_ and len(self.fillValues_) < ecount:
			raise ExplainFixException("errFillCount", col=self.key, cls=self.clsName, count=ecount)
		self.__splitters = self.query("arrSplitters", (str,))					# 元组分隔符，可以被子类对象修改
		self.__tupleScopeStarts = self.query("tupleScopeStarts", (str, ))	# 元组区间起始符，可以被子类对象修改
		self.__tupleScopeEnds = self.query("tupleScopeEnds", (str, ))		# 元组区间结束符，可以被子类对象修改
		self.__listScopeStarts = self.query("listScopeStarts", (str, ))		# 列表区间起始符，可以被子类对象修改
		self.__listScopeEnds = self.query("listScopeEnds", (str, ))			# 列表区间结束符，可以被子类对象修改


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __explainArrayTypeText(self, dsrc, row):
		"""
		返回：(列表类型, Excel 格子中填写的字符串)
		"""
		vtype = tuple
		text = self.getCellText_(dsrc, row).strip()
		cutted, text = utils.cutStarts(text, self.__listScopeStarts)
		if cutted:
			cutted, text = utils.cutEnds(text, self.__listScopeEnds)
			if not cutted:
				raise ExplainErrorValueTypeException(dsrc, row, self.key)
			vtype = list
		else:
			cutted, text = utils.cutStarts(text, self.__tupleScopeStarts)
			if cutted:
				cutted, text = utils.cutEnds(text, self.__tupleScopeEnds)
				if not cutted:
					raise ExplainErrorValueTypeException(dsrc, row, self.key)
		text = utils.cutEnds(text, self.__splitters)[1]
		return vtype, text.strip()


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getStrElements_(self, dsrc, row):
		"""
		获取字符串形式的每个元素
		"""
		vtype, text = self.__explainArrayTypeText(dsrc, row)
		if text == "": return vtype()
		elems = utils.splits(text, self.__splitters)
		if vtype is list: return elems
		return vtype(elems)

	def str2value_(self, index, text):
		"""
		获取指定元素的值
		"""
		return text

	# -------------------------------------------------
	def filter_(self, dsrc, row, arrayType, value=ex_base.INNER):
		if value is ex_base.INNER:												# 解释内容为空
			if self.isExcludeValue_():											# 有排除值
				return ABANDON_COL
			elif self.defValue_ is not ex_base.INNER:							# 有默认值
				return self.fnRet(self.defValue_)
			elif self.ecount_ < 1:												# 没有元素个数限定
				return self.fnRet(arrayType())
			return ExplainErrorValueTypeException(dsrc, row, self.key)			# 有限定个数，却不填任何值
		elif self.isExcludeValue_(value):										# 解释内容与排除值相等
			return ABANDON_COL
		elif value is ex_base.ERR_TYPE:											# 解释内容类型不正确
			raise ExplainErrorValueTypeException(dsrc, row, self.key)
		return self.fnRet(value)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __call__(self, dsrc, row):
		strElems = self.getStrElements_(dsrc, row)
		arrayType = type(strElems)
		count = len(strElems)
		if count == 0:															# 不填写内容
			return self.filter_(dsrc, row, arrayType)

		elems = []
		for index, strElem in enumerate(strElems):
			value = self.str2value_(index, strElem)
			if value == ex_base.ERR_TYPE:
				raise ExplainErrorValueTypeException(dsrc, row, self.key)
			elems.append(value)

		if self.ecount_ > 0:													# 元素个数固定
			if count > self.ecount_:											# 填写元素过多，被截断
				elems = elems[:self.ecount_]
			elif count < self.ecount_:											# 填写元素不够
				if self.fillValues_:											# 需要填充
					for idx in xrange(count, self.ecount_):
						elems.append(self.fillValues_[idx])
				else:
					raise ExplainErrorValueTypeException(dsrc, row, self.key)	# 填写元素不够，但不要求填充
		if arrayType is tuple:
			elems = tuple(elems)												# 元素个数不固定
		return self.filter_(dsrc, row, arrayType, elems)


# ------------------------------------------------------------------------------
# 指定列为一个“固定类型元素”的元组或列表
# ------------------------------------------------------------------------------
class ex_onetype_array_col(ex_array_col_base):
	def __init__(self, key, etype, ecount=0, defValue=ex_base.INNER, **extras):
		ex_array_col_base.__init__(self, key, ecount, defValue, **extras)
		self.__etype = etype


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def str2value_(self, index, text):
		try: return self.__etype(text)
		except: return ex_base.ERR_TYPE


# --------------------------------------------------------------------
# 指定列为一个“固定类型元素”的元组或列表解释器枚举
# --------------------------------------------------------------------
class ex_str_array_col(ex_onetype_array_col):
	"""
	字符串型 tuple/list
	"""
	def __init__(self, key, ecount=0, defValue=ex_base.INNER, **extras):
		ex_onetype_array_col.__init__(self, key, str, ecount, defValue, **extras)

	def str2value_(self, index, text):
		return text

class ex_stpl_array_col(ex_str_array_col):
	"""
	字符串模板型 string.Template
	"""
	def str2value_(self, index, text):
		return StringTemplate(text)

class ex_bool_array_col(ex_onetype_array_col):
	def __init__(self, key, ecount=0, defValue=ex_base.INNER, **extras):
		ex_onetype_array_col.__init__(self, key, bool, ecount, defValue, **extras)
		self.trueSigns_ = self.query("trues", (str,))		# 可以被子类修改
		self.falseSigns_ = self.query("falses", (str,))		# 可以被子类修改

	def str2value_(self, index, text):
		if text.isdigit(): return bool(int(text))
		elif text in self.trueSigns_: return True
		elif text in self.falseSigns_: return False
		return ex_base.ERR_TYPE


class ex_int_array_col(ex_onetype_array_col):
	"""
	整型 tuple/list
	"""
	def __init__(self, key, ecount=0, defValue=ex_base.INNER, **extras):
		ex_onetype_array_col.__init__(self, key, int, ecount, defValue, **extras)

class ex_enum_array_col(ex_int_array_col):
	"""
	枚举类型 tuple/list
	"""
	def __init__(self, key, enums, ecount=0, defValue=ex_base.INNER, **extras):
		ex_int_array_col.__init__(self, key, ecount, defValue, **extras)
		self.__enums = tuple(enums)

	def filter_(self, dsrc, row, arrayType, value=ex_base.INNER):
		value = ex_int_array_col.filter_(self, dsrc, row, arrayType, value)
		if value != ex_base.INNER:
			for e in value:
				if e not in self.__enums:
					raise ExplainEnumValueException(dsrc, row, self.key, self.__enums)
		return value

class ex_hlint_array_col(ex_onetype_array_col):
	"""
	默认值为 0x0 的十六进制整型 tuple/list，可以通过传入 defValue 修改默认值
	extras 中增加以下键值：
		hexSites: 类型为整形，表示最少为多少位的十六进制整形，如果位数不够，则高位补 0。
			例如：如果 hexSites = 4，而解释的结果值为 0x4f，则导出结果为 0x004f
	"""
	def __init__(self, key, ecount=0, defValue=ex_base.INNER, **extras):
		"""
		sites 表示十六进制的位数，如果不够 sites 位，则高位补 0
		"""
		ex_onetype_array_col.__init__(self, key, hlint, ecount, defValue, **extras)
		self.__hexSites = extras.get("hexSites", 0)

	def str2value_(self, index, text):
		try: return hlint(text, self.__hexSites)
		except ValueError: return ex_base.ERR_TYPE

class ex_henum_array_col(ex_hlint_array_col):
	"""
	枚举类型 tuple/list
	"""
	def __init__(self, key, enums, ecount=0, defValue=ex_base.INNER, **extras):
		ex_hlint_array_col.__init__(self, key, ecount, defValue, **extras)
		self.__enums = tuple(enums)

	def filter_(self, dsrc, row, arrayType, value=ex_base.INNER):
		value = ex_hlint_array_col.filter_(self, dsrc, row, arrayType, value)
		if value != ex_base.INNER:
			for e in value:
				if e not in self.__enums:
					raise ExplainEnumValueException(dsrc, row, self.key, self.__enums)
		return value

class ex_float_array_col(ex_onetype_array_col):
	"""
	浮点型 tuple/list
	"""
	def __init__(self, key, ecount=0, defValue=ex_base.INNER, **extras):
		ex_onetype_array_col.__init__(self, key, float, ecount, defValue, **extras)


class ex_xfloat_array_col(ex_onetype_array_col):
	"""
	可指定小数点位数的浮点型 tuple/list
	"""
	def __init__(self, key, ecount=0, defValue=ex_base.INNER, **extras):
		dds = extras.get("decimalDigits", CustomConfig().query("explainer/decimalDigits", int))
		ex_onetype_array_col.__init__(self, key, xfloat[dds], ecount, defValue, **extras)


# ------------------------------------------------------------------------------
# 指定列为一个元素不确定类型的元组或列表
# ------------------------------------------------------------------------------
class ex_multitype_array_col(ex_array_col_base):
	"""
	etypes 为每个元素指出各自的类型，并限定了元素的个数为 len(etypes)
	"""
	__validTypes = (str, bool, int, long, hlint, float, xfloat)

	def __init__(self, key, etypes, defValue=ex_base.INNER, **extras):
		ex_array_col_base.__init__(self, key, len(etypes), defValue, **extras)
		self.trueSigns_ = self.query("trues", (str,))		# 可以被子类修改
		self.falseSigns_ = self.query("falses", (str,))		# 可以被子类修改
		self.__etypes = etypes

	# -------------------------------------------------
	# protected
	# -------------------------------------------------
	def str2value_(self, index, text):
		etype = self.__etypes[index]
		if etype not in self.__validTypes:
			raise ExplainFixException("errUnsupportType", cls=self.clsName, type=etype)
		if etype is str:
			return text
		elif etype is bool:
			if text.isdigit(): return bool(int(text))
			elif text in self.trueSigns_: return True
			elif text in self.falseSigns_: return False
			return ex_base.ERR_TYPE
		try:
			return etype(text)
		except:
			return ex_base.ERR_TYPE
