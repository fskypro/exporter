# -*- coding: utf-8 -*-
#

"""
对应表格中一列，并且以指定类型返回的解释器

如：
  key   str   int
|-----|-----|-----|
|  1  | XXX |  22 |
|-----|-----|-----|
|  2  | YYY |  55 |
|-----|-----|-----|

writen by yongwei-huang -- 2013.04.12
"""

from config.CustomConfig import CustomConfig
from libs.custom_types.hlint import hlint
from libs.custom_types.xfloat import xfloat
from CustomTypes import StringTemplate
from ExplainExceptions import ExpressionException
from ExplainExceptions import ExplainErrorValueTypeException
from ExplainExceptions import ExplainEnumValueException
from ex_base import ex_base
from ex_base import ex_col_base


# --------------------------------------------------------------------
# 对应表格中一列，并且以指定类型返回的解释器
# --------------------------------------------------------------------
class ex_value_col_base(ex_col_base):
	"""
	将某列值解释为指定类型的单个值基类，返回 etype 参数指定的类型值
	构造函数参数说明：
	key：对应 Excel 表格中某一列的列名
	etype：该列内容要作为什么类型解释，它是一个类型参数，如：flaot，int 等
	defValue：可以传入以下内容：
		1、不传入任何值：这样如果 Excel 格子中不填写内容，则会抛出 ExplainErrorValueTypeException 异常，表示 Excel 格子填写错误
		2、传入其他值：这样如果 Excel 格子中不填写内容，则会以该值作为结果返回
		注意：如果以指定类型解释内容错误，将会抛出 ExplainErrorValueTypeException 异常
			如 etype 为 int，但 Excel 表格中填写了“aa”，则会抛出 ExplainErrorValueTypeException 异常
	extras：包含以下可选键：
		fixValues：列出一组校验值，使得解释出来的内容必须从这组值中抽取，否则抛出 ExplainErrorValueTypeException 异常
	"""
	def __init__(self, key, etype, defValue=ex_base.INNER, **extras):
		ex_col_base.__init__(self, key, defValue, **extras)
		self.__etype = etype
		fixValues = extras.get("fixValues", ex_base.INNER)
		if (fixValues is not ex_base.INNER) and (not iterable(fixValues)):
			raise ExpressionException("extra argument 'fixValues' of '%s' must be an iterable object, but not %r" % (self.key, fixValues))
		self.__fixValues = fixValues


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def str2value_(self, text):
		try: return self.__etype(text)
		except: return ex_base.ERR_TYPE


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __call__(self, dsrc, row):
		text = self.getCellText_(dsrc, row)
		if text == "": return self.filter_(dsrc, row)						# 表格不填写任何内容
		value = self.filter_(dsrc, row, self.str2value_(text))
		if self.__fixValues is not ex_base.INNER and \
			value not in self.__fixValues:
				raise ExplainErrorValueTypeException(dsrc, row, self.key)
		return value


# --------------------------------------------------------------------
# 单列元素值（枚举具体类型）解释器
# --------------------------------------------------------------------
class ex_str_col(ex_value_col_base):
	"""
	可设置空值默认值的字符串
	defValue 参数：
		1、不传入任何值时：如果 Excel 表格中不填写任何内容，则会抛出 ExplainErrorValueTypeException 异常
		2、传入一个值时：如果 Excel 表格中不填写任何内容，则会返回该值
	与 ex_orign_col 的区别是：
		假使 Excel 格子中不填写任何内容
		对于 ex_orign_col，它会返回一个空串作为结果。
		对于 ex_str_col，它会返回 defValue 参数指定的默认值，如果 defValue 参数不传入任何值，则会抛出 ExplainErrorValueTypeException 异常
	"""
	def __init__(self, key, defValue=ex_base.INNER, **extras):
		ex_value_col_base.__init__(self, key, str, defValue, **extras)

	def str2value_(self, text):
		return text

class ex_stpl_col(ex_str_col):
	"""
	解释为字符串模板的列
	"""
	def str2value_(self, text):
		return StringTemplate(text)

class ex_bool_col(ex_value_col_base):
	"""
	返回默认值为 False 的布尔型
	在 Excel 表格中可以填写一个整数表示布尔值，0 被解释为 False，其他整形值被解释为 True
	在 Excel 表格中还可以填写别的内容表示 True 或 False，这些内容可以在 config.xml 中指定，
		也可以通过子类修改 trueSigns_ 和 falseSigns_ 成员做到
	"""
	def __init__(self, key, defValue=False, **extras):
		ex_value_col_base.__init__(self, key, bool, defValue, **extras)
		self.trueSigns_ = self.query("trues", (str,))		# 可以被子类修改
		self.falseSigns_ = self.query("falses", (str,))		# 可以被子类修改

	def str2value_(self, text):
		if text.isdigit(): return bool(int(text))
		elif text in self.trueSigns_: return True
		elif text in self.falseSigns_: return False
		return ex_base.ERR_TYPE


class ex_int_col(ex_value_col_base):
	"""
	返回默认值为 0 的整型，默认值可以通过参数 defValue 重新指定
	"""
	def __init__(self, key, defValue=0, **extras):
		ex_value_col_base.__init__(self, key, int, defValue, **extras)

class ex_enum_col(ex_int_col):
	"""
	返回在指定的一组范围内的整型，默认值可以通过参数 defValue 重新指定
	通过 enums 参数指定一个取值范围，如果不指定 enums，则与 ex_int_col 一样
	如果表格中填写的枚举值不正确，将会抛出 异常
	"""
	def __init__(self, key, enums, defValue=ex_base.INNER, **extras):
		ex_int_col.__init__(self, key, defValue=defValue, **extras)
		self.__enums = tuple(enums)

	def filter_(self, dsrc, row, value=ex_base.INNER):
		value = ex_int_col.filter_(self, dsrc, row, value)
		if value == ex_base.INNER:
			value = self.__enums[0]
		elif value not in self.__enums:
			raise ExplainEnumValueException(dsrc, row, self.key, self.__enums)
		return value

class ex_hlint_col(ex_value_col_base):
	"""
	默认值为 0x0 的十六进制整型，默认值也可以通过 defValue 参数修改
	sites 参数表示对十六进制数的位数进行整齐化，如：
		site 为 4 时，如果值为 0x1 则，输出为：0x0001，如果值为 0x00001，则输出仍为：0x00001
	"""
	def __init__(self, key, defValue=0, sites=0, **extras):
		ex_value_col_base.__init__(self, key, hlint, hlint(defValue, sites), **extras)
		self.__sites = sites

	def str2value_(self, text):
		try: return hlint(text, self.__sites)
		except ValueError: return ex_base.ERR_TYPE


class ex_float_col(ex_value_col_base):
	"""
	默认值为 0.0 的浮点数，也可以通过传入 defValue 参数修改默认值
	"""
	def __init__(self, key, defValue=0.0, **extras):
		ex_value_col_base.__init__(self, key, float, defValue, **extras)


class ex_xfloat_col(ex_value_col_base):
	"""
	可以指定取小数点后几位的的浮点数，可以通过传入 defValue 参数修改默认值
	"""
	def __init__(self, key, defValue=0.0, **extras):
		dds = extras.get("decimalDigits", CustomConfig().query("explainer/decimalDigits", int))
		if type(defValue) is float:
			self.defValue_ = xfloat[dds](defValue)
		ex_value_col_base.__init__(self, key, xfloat[dds], defValue, **extras)


class ex_scale_col(ex_float_col):
	"""
	默认值为 1.0 的浮点解释器
	"""
	def __init__(self, key, **extras):
		ex_float_col.__init__(self, key, 1.0, **extras)
