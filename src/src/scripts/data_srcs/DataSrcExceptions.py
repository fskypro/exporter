# -*- coding: utf-8 -*-
#

"""
自定义数据源异常

2011.09.20: writen by hyw
"""

import TextEncoder
from config.Local import Local
from Exceptions import BaseException


# ------------------------------------------------------------------------------
# 数据源异常
# ------------------------------------------------------------------------------
class DataSourceException(BaseException):
	"""
	操作数据源异常
	"""
	def __init__(self, msg):
		title = Local().formatLocalText("dataSource", 'errTitle')
		BaseException.__init__(self, title, msg)

class DataSourceFixException(DataSourceException):
	"""
	知道明确错误的操作数据源异常
	"""
	def __init__(self, tagName, **args):
		msg = Local().formatLocalText("dataSource", tagName, **args)
		DataSourceException.__init__(self, msg)


# ------------------------------------------------------------------------------
# 具体数据源异常
# ------------------------------------------------------------------------------
# --------------------------------------------------------------------
# csv file
# --------------------------------------------------------------------
class CSVException(DataSourceException):
	"""
	操作 csv 相关异常
	"""
	def __init__(self, msg):
		DataSourceException.__init__(self, msg)

# -----------------------------------------------------
class CSVFixException(CSVException):
	"""
	明确的操作 CSV 相关异常
	"""
	def __init__(self, tagName, **args):
		msg = Local().formatLocalText("csvApp", tagName, **args)
		CSVException.__init__(self, msg)


# --------------------------------------------------------------------
# excelApp 异常
# --------------------------------------------------------------------
class ExcelComException(DataSourceException):
	"""
	操作 Excel 时，Com 组件系统发出的异常
	"""
	def __init__(self, errInfos):
		"""
		errInfos 为读 excel 时，系统抛出异常信息，是个链表
		"""
		errs = []
		self.__exportError(errInfos, errs)
		msg = "\n".join(errs)
		DataSourceException.__init__(self, msg)

	def __exportError(self, errInfos, errs):
		for errInfo in errInfos:
			etype = type(errInfo)
			if etype is tuple:
				self.__exportError(errInfo, errs)
			elif isinstance(etype, basestring):
				try: text = TextEncoder.sys2script(errInfo)
				except: text = errInfo
				errs.append("  " + text)

class ExcelInEditException(ExcelComException):
	"""
	Excel 表格可能处于被编辑状态
	"""
	def __init__(self, errInfos):
		msg = Local().formatLocalText("excelApp", 'errInEdit')
		if type(errInfos) is tuple: errInfos += (msg, )
		else: errInfos = (errInfos, msg)
		ExcelComException.__init__(self, errInfos)

# -----------------------------------------------------
class ExcelFixException(DataSourceException):
	"""
	操作 Excel 时，能明确知道原因的异常
	"""
	def __init__(self, tagName, **args):
		msg = Local().formatLocalText("excelApp", tagName, **args)
		DataSourceException.__init__(self, msg)
