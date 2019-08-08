# -*- coding: utf-8 -*-
#

"""
元素值解释器基类

writen by yongwei-huang -- 2013.04.12
"""

import weakref
from define import ABANDON_COL
from config.CustomConfig import CustomConfig
from data_srcs.DataSource import iDataSource
from Exceptions import BaseException
from ExplainExceptions import ExplainTextError
from ExplainExceptions import ExplainFixException
from ExplainExceptions import ExplainErrorValueTypeException


# --------------------------------------------------------------------
# 顶层基类，不能实例化
# extras 参数囊括 config.xml 中标签 explainer 下的子标签。
# 同时可以有以下 key：
#     excludeValue：表示如果表格中的内容解释后值等于 excludeValue，则不导出
#         excludeValue 可以是一个可调用对象，如果是可调用对象，则包含一个参数表示解释到的值
#     fnRet：这是一个回调，在 __call__ 返回之前调用一下 fnRet，并把 fnRet 的返回作为返回结果
#         fnRet 包含一个参数，表示解释后返回的结果
# --------------------------------------------------------------------
class ex_base(object):
	class INNER: pass
	class ERR_TYPE: pass

	"""
	解释器基类，不一定对应 Excel 表格中任何一列
	"""
	def __init__(self, defValue=INNER, **extras):
		self.defValue_ = defValue
		self.__userData = ex_base.INNER
		self.__extras = extras

	def __getitem__(self, args):
		self.__userData = args
		return self

	def __call__(self, dsrc, row):
		raise BaseException("Error", "class %r must implement %r method" % (self.clsName, "__call__"))

	@staticmethod
	def __fnRet(x):
		return x

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def clsName(self):
		return self.__class__.__name__

	@property
	def defValue(self):
		return self.defValue_

	@property
	def excludeValue(self):
		return self.__extras.get("excludeValue", self.INNER)

	@property
	def fnRet(self):
		return self.__extras.get("fnRet", ex_base.__fnRet)

	@property
	def userData(self):
		return self.__userData


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def isExcludeValue_(self, value=INNER):
		"""
		判断给定的值是否与构造函数中传入的 excludeValue 一致
		"""
		if value is self.INNER:									# 解释内容为空
			return self.excludeValue is not self.INNER			# excludeValue 不传入返回 False
		excludeValue = self.excludeValue
		if excludeValue is self.INNER:
			return False
		if callable(excludeValue):
			return excludeValue(value)
		return excludeValue == value


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def query(self, attrName, attrType):
		"""
		获取构造函数中传入的额外属性值，如果这些属性值不存在，则会从 outItemInfo 的 query 中取
		"""
		value = self.__extras.get(attrName, self.INNER)
		if value is not self.INNER: return value
		value = CustomConfig().query("explainer/%s" % attrName, attrType)
		self.__extras[attrName] = value
		return value

	@classmethod
	def explainText(cls, text, *args, **extras):
		raise BaseException("Error", "%s unimplements a class method: %s" % \
			(cls.__name__, 'explainText(cls, text, *args, **extras)'))


# --------------------------------------------------------------------
# 解释器对应表格中一列的基类
# --------------------------------------------------------------------
class ex_col_base(ex_base):
	"""
	对应 Excel 表格中某一列的解释器
	key 为指定列的列名
	"""
	def __init__(self, key, defValue=ex_base.INNER, **extras):
		ex_base.__init__(self, defValue, **extras)
		if key is not ex_base.INNER:
			key = key.strip()
			if key == "":
				raise ExplainFixException("errEmptyKey", cls=self.clsName)
		self.key = key
		self.__mapCol = -1					# 对应的列索引（解释的时候由 exporter/exporter.py 中设置）


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getColIndex_(self, dsrc):
		"""
		获取本列对应的列号
		"""
		mapCol = self.__mapCol
		if mapCol < 0:
			mapCol = dsrc.name2col(self.key)
			self.__mapCol = mapCol
		return mapCol

	def getCellText_(self, dsrc, row):
		"""
		获取本列指定行的内容
		"""
		col = self.getColIndex_(dsrc)
		return dsrc.getText(row, col)

	# -------------------------------------------------
	def filter_(self, dsrc, row, value=ex_base.INNER):
		"""
		如果构造函数中传入 extra 的参数带有 excludeValue 则：
			1、如果解释内容为空，则返回 ABANDON_COL
			2、如果解释内容与 exclueValue 值相等，则返回 ABANDON_COL
		如果构造函数中传入的 extra 参数中没带有 excludeValue 则：
			1、如果解释内容为空，同时传入了 defValue，则返回 defValue
			2、如果解释内容为空，但没传入 defValue，则抛出 ExplainErrorValueTypeException 异常
		"""
		if value is ex_base.INNER:											# 解释内容为空
			if self.excludeValue is not ex_base.INNER:						# 有排除值
				return ABANDON_COL
			elif self.defValue_ is ex_base.INNER:							# 没有传入默认值
				raise ExplainErrorValueTypeException(dsrc, row, self.key)
			return self.fnRet(self.defValue_)
		elif self.isExcludeValue_(value):									# 解释内容与排除值相等
			return ABANDON_COL
		elif value is ex_base.ERR_TYPE:										# 解释内容类型不正确
			raise ExplainErrorValueTypeException(dsrc, row, self.key)
		return self.fnRet(value)

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def explainText(cls, text, *args, **extras):
		"""
		利用该解释器脱离数据源解释给出的文本
		如果解释失败，将会抛出 ExplainTextError 异常
		"""
		class DataSource(iDataSource):
			def __init__(self, text):
				self.__text = text
				iDataSource.__init__(self, 0, 0, 0)
				self.name2col_[ex_base.INNER] = 0
			rowCount = property(lambda self: 1)
			colCount = property(lambda self: 1)
			def getText(self, row, col): return self.__text
			def setText(self, row, col, text): self.__text = text
			def getRangeText(self, row1, col1, row2, col2): return [[self.__text]]
			def setRangeText(self, row, col, datas): self.__text = datas[0][0]
			def iterColText(self, col): yield self.__text
			def iterRowText(self, row): yield self.__text
			def iterRangeText(self, row1, col1, row2, col2): yield self.__text
			def getSrcText(self): return self.__text

		inst = cls(ex_base.INNER, *args, **extras)
		inst.getCellText_ = lambda dsrc, row: text
		try:
			return inst(DataSource(text), 0)
		except ExplainErrorValueTypeException:
			raise ExplainTextError(inst, text)


# --------------------------------------------------------------------
# 解释器对应表格中一列，并且以字符串形式返回表格中原始值
# --------------------------------------------------------------------
class ex_orign_col(ex_col_base):
	"""
	以字符串形式直接返回格子内容，如果格子不填写任何内容，则返回空字符串
	"""
	def __init__(self, key, **extras):
		ex_col_base.__init__(self, key, **extras)

	def __call__(self, dsrc, row):
		value = self.getCellText_(dsrc, row)
		return self.filter_(dsrc, row, value)
