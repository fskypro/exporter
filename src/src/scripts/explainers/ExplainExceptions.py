# -*- coding: utf-8 -*-
#

"""
解释表格内容异常

2011.09.20: writen by hyw
"""

from config.Local import Local
from Exceptions import BaseException

class ExpressionException(BaseException):
	"""
	导出表达式异常
	"""
	def __init__(self, msg):
		title = Local().formatLocalText("expression", "errTitle")
		BaseException.__init__(self, title, msg)

class ExplainException(BaseException):
	"""
	用户解释数据异常
	"""
	def __init__(self, msg):
		title = Local().formatLocalText("explain", "errTitle")
		BaseException.__init__(self, title, msg)

class ExplainFixException(ExplainException):
	"""
	能明确知道错误的解释表格异常
	"""
	def __init__(self, tag, **args):
		msg = Local().formatLocalText("explain", tag, **args)
		ExplainException.__init__(self, msg)

class ExplainErrorValueTypeException(ExplainFixException):
	"""
	excel 表格格子内容类型不正确异常
	"""
	def __init__(self, dsrc, row, colName):
		"""
		row 为行号，第一行为 0
		colName 为列名
		"""
		ExplainFixException.__init__(self, "errType", table=dsrc.getSrcText(), \
			row=row+1, col=colName, text=dsrc.getText(row, colName))

class ExplainEnumValueException(ExplainFixException):
	"""
	excel 表格格子内容枚举值不正确异常
	"""
	def __init__(self, dsrc, row, colName, enums):
		"""
		row 为行号，第一行为 0
		colName 为列名
		enums 所有允许的枚举集合
		"""
		ExplainFixException.__init__(self, "errEnumType", table=dsrc.getSrcText(), \
			row=row+1, col=colName, text=dsrc.getText(row, colName), enums=str(enums))

class ExplainTextError(ExplainException):
	"""
	用解释器解释指定的一段文本异常
	"""
	def __init__(self, exp, text):
		ExplainFixException.__init__(self, "errExplainText", exp=exp.clsName, text=text)
