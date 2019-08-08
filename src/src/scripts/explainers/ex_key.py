# -*- coding: utf-8 -*-
#

"""
字典最外层键的表达式

导 Excel 表格主键（导出字典最外层键）解释器
如果要忽略 Excel 表格中的某行，则在 Excel 表格中该行主键列处填写入
    config.xml 中 explainer/ignorSign 标签所指定的字符串
    该行被忽略后，键解释器将需要返回 KEYRET_IGNOR
如果 Excel 表格表格中的某行，其主键列处不填写任何内容，则该行将会被忽略
    键解释器需要返回 KEYRET_EMPTY

writen by yongwei-huang -- 2013.04.12
"""

import utils
from libs.custom_types.hlint import hlint
from define import KEYRET_EMPTY				# 键返回此值表示该行键为空
from define import KEYRET_IGNOR				# 键返回此值表示该行忽略（不导出）
from ExplainExceptions import ExplainFixException
from ExplainExceptions import ExplainErrorValueTypeException
from ex_base import ex_base
from ex_base import ex_col_base
from ex_base import ex_orign_col
from ex_array_col import ex_array_col_base


# --------------------------------------------------------------------
# 将一个列解释为导出字典的主键
# --------------------------------------------------------------------
class ex_key_col(ex_col_base):
	"""
	ktype 指定键的类型
	"""
	def __init__(self, key, ktype, **extras):
		ex_col_base.__init__(self, key, **extras)
		self.__ktype = ktype

	def __call__(self, dsrc, row):
		text = self.getCellText_(dsrc, row)
		if text == "":
			return KEYRET_EMPTY
		if text == self.query("ignorSign", str):
			return KEYRET_IGNOR
		value = self.str2value_(text)
		if value == ex_base.ERR_TYPE:
			raise ExplainErrorValueTypeException(dsrc, row, self.key)
		return self.fnRet(value)

	def str2value_(self, text):
		try: return self.__ktype(text)
		except: return ex_base.ERR_TYPE


# --------------------------------------------------------------------
# 解释指定列为一个字符串，将其返回作为最外层字典键的解释器
# --------------------------------------------------------------------
class ex_key_str_col(ex_key_col):
	def __init__(self, key, **extras):
		ex_key_col.__init__(self, key, str, **extras)

	def str2value_(self, text):
		return text

# --------------------------------------------------------------------
# 解释指定列为一个整型，将其返回作为最外层字典键的解释器
# --------------------------------------------------------------------
class ex_key_int_col(ex_key_col):
	def __init__(self, key, **extras):
		ex_key_col.__init__(self, key, int, **extras)


# --------------------------------------------------------------------
# 解释指定列为一个十六进制整型，将其返回作为导出字典键的解释器
# --------------------------------------------------------------------
class ex_key_hlint_col(ex_key_col):
	def __init__(self, key, sites=0, **extras):
		ex_key_col.__init__(self, key, hlint, **extras)
		self.__sites = sites

	def str2value_(self, text):
		try: return hlint(text, self.__sites)
		except: return ex_base.ERR_TYPE


# --------------------------------------------------------------------
# 解释指定列为一个元组，并将其作为导出字典主键的解释器
# --------------------------------------------------------------------
class ex_key_tuple_col(ex_array_col_base):
	"""
	支持的类型有：str/bool/int/hlint
	"""
	__validTypes = (str, bool, int, long, hlint)

	def __init__(self, key, types, **extras):
		ex_array_col_base.__init__(self, key, len(types), **extras)
		self.__ktypes = types
		self.__ecount = len(types)
		self.trueSigns_ = self.query("trues", (str,))		# 可以被子类修改
		self.falseSigns_ = self.query("falses", (str,))		# 可以被子类修改

	def __call__(self, dsrc, row):
		text = self.getCellText_(dsrc, row)
		if text == "": return KEYRET_EMPTY
		if text == self.query("ignorSign", str):
			return KEYRET_IGNOR
		strElems = utils.splits(text, self.splitters_)
		if len(strElems) < self.__ecount:
			raise ExplainErrorValueTypeException(dsrc, row, self.key)
		key = []
		for idx, ktype in enumerate(self.__ktypes):
			value = ktype(ktype, strElems[idx])
			if value == ex_base.ERR_TYPE:
				raise ExplainErrorValueTypeException(dsrc, row, self.key)
			key.append(value)
		return tuple(key)

	def str2value_(self, ktype, text):
		if ktype not in self.__validTypes:
			raise ExplainFixException("errUnsupportType", cls=self.clsName, type=ktype)
		if ktype is str:
			return text
		elif ktype is bool:
			if text.isdigit(): return bool(int(text))
			elif text in self.trueSigns_: return True
			elif text in self.falseSigns_: return False
			return ex_base.ERR_TYPE
		try:
			return ktype(text)
		except:
			return ex_base.ERR_TYPE


# --------------------------------------------------------------------
# 解释多列后，将其组成一个元组作为导出字典的主键
# --------------------------------------------------------------------
class ex_key_cols(ex_base):
	"""
	解释多列后，将其组成一个元组作为导出字典的主键
	支持的类型有：str, int, long, hlint
	"""
	__validTypes = (str, bool, int, long, hlint)

	def __init__(self, key_type, *key_types, **extras):
		"""
		key_type 参数为：(Excel表格中的某列名, 该列类型)
		key_types 参数为不定个 key_type
		"""
		ex_base.__init__(self, **extras)
		key_types = list(key_types)
		key_types.insert(0, key_type)
		self.__ftrans = []
		for key, etype in key_types:
			self.__ftrans.append((ex_orign_col(key), etype))

	def __call__(self, dsrc, row):
		elems = []
		for ftran, etype in self.__ftrans:
			text = ftran(dsrc, row)
			if text == self.query("ignorSign", str):
				return KEYRET_IGNOR
			if text == "": return KEYRET_EMPTY
			value = self.str2value_(etype, text)
			if value == ex_base.ERR_TYPE:
				raise ExplainErrorValueTypeException(dsrc, row, self.key)
			elems.append(value)
		return tuple(elems)

	def str2value_(self, etype, text):
		if etype not in self.__validTypes:
			raise ExplainFixException("errUnsupportType", cls=self.clsName, type=etype)
		if etype is str: return text
		try: return etype(text)
		except: return ex_base.ERR_TYPE


# --------------------------------------------------------------------
# 返回 Excel 表格中当前号（减去一个指定偏移）作为键的解释器
# --------------------------------------------------------------------
class ex_key_row(ex_base):
	def __init__(self, offset=0, **extras):
		ex_base.__init__(self, **extras)
		self.__offset = offset

	def __call__(self, dsrc, row):
		return row - self.__offset
