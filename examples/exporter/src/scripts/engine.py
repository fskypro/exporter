# -*- coding: utf-8 -*-
#

"""
2012.12.23: writen by hyw
"""

import sys
from libs.Singleton import Singleton

VERSION = "4.0.0"

# ------------------------------------------------------------------------------
# globals
# ------------------------------------------------------------------------------
class _Caller(object):
	def __init__(self):
		self.__cbs = []

	def __call__(self, *args, **dargs):
		for cb in self.__cbs:
			try:
				cb(*args, **dargs)
			except Exception, err:
				sys.excepthook(Exception, err, sys.exc_traceback)

	def bind(self, cb):
		if cb not in self.__cbs:
			self.__cbs.append(cb)

	def unbind(self, cb):
		if cb in self.__cbs:
			self.__cbs.remove(cb)


class Listener(Singleton):
	__cbs = {
		"cbInfo": _Caller(),						# 发出提示时被调用（参数：提示信息）
		"cbWarning": _Caller(),						# 发出警告时被调用（参数：警告信息）
		"cbError": _Caller(),						# 发出错误时被调用（参数：错误信息）
		"cbLocalMsg": _Caller(),					# 发出提示时被调用（参数：1、语言配置中的主标签；2、语言配置中的副标签；3、字典格式化参数）

		# ----------------------------------------
		"cbBeginLoadDataSource": _Caller(),			# 开始加载数据源时被调用（参数：1、data_srcs/LoadDataTracer）
		"cbLoadingDataSource": _Caller(),			# 加载数据源进度回调（参数：1、data_srcs/LoadDataTracer；2、progress）
		"cbEndLoadDataSource": _Caller(),			# 结束加载数据源时被调用（参数：1、data_srcs/LoadDataTracer）

		# ----------------------------------------
		"cbBeginExport": _Caller(),					# 开始导出模板时被调用（参数：导出模板）
		"cbEndExport": _Caller(),					# 结束导出模板时被调用（参数：导出模板）

		"cbBeginExportOutInfo": _Caller(),			# 开始导出模板中指定的一个配置时被调用（参数：exporter/ExportTracers::ExportTracer）
		"cbEndExportOutInfo": _Caller(),			# 结束导出模板中指定的一个配置时被调用（参数：exporter/ExportTracers::ExportTracer）

		"cbBeginExportOutItemInfo": _Caller(),		# 开始导出配置中的一个表达式时被调用（参数：exporter/ExportTracers::ExportItemTracer）
		"cbEndExportOutItemInfo": _Caller(),		# 结束导出配置中的一个表达式时被调用（参数：exporter/ExportTracers::ExportItemTracer）

		"cbBeginScanExp":  _Caller(),				# 开始扫描一个导出表达式所涉及的所有数据源（参数：exporter/ExportTracers::ScanExpTracer）
		"cbEndScanExp":  _Caller(),					# 结束扫描一个导出表达式所涉及的所有数据源（参数：exporter/ExportTracers::ScanExpTracer）

		"cbBeginScanDataSource": _Caller(),			# 开始扫描一个数据源时被调用（参数：exporter/ExportTracers::ScanDataSourceTracer）
		"cbScanningDataSource": _Caller(),			# 扫描数据源进度侦测回调（参数：1、exporter/ExportTracers::ScanDataSourceTracer；2、当前行号）
		"cbEndScanDataSource": _Caller(),			# 结束扫描一个数据源时被调用（参数：exporter/ExportTracers::ScanDataSourceTracer）

		"cbBeginWriteOutItemInfo": _Caller(),		# 开始写出配置时被调用（参数：exporter/ExportTracers::WriteItemTracer）
		"cbWritingOutItemInfo": _Caller(),			# 写出配置进度侦测回调（参数：1、exporter/ExportTracers::WriteItemTracer；2、当前记录索引）
		"cbEndWriteOutItemInfo": _Caller(),			# 结束写出配置时被调用（参数：exporter/ExportTracers::WriteItemTracer）

		# ----------------------------------------
		"cbExcelAppReleased": _Caller(),			# 释放 EXCEL 操作权时被调用（参数：无）
		"cbExcelWalkBookClosed": _Caller(),			# EXCEL 工作簿关闭时被调用（参数：1、工作簿；2、失败信息，关闭成功则为 None）

		# ----------------------------------------
		"cbAppExit": _Caller(),						# 程序退出时被调用（参数：退出代码，0 为正常退出，其他值代表不同意义）
	}

	def __init__(self):
		pass


	def __getattribute__(self, attrName):
		return object.__getattribute__(self, attrName)

	def __getattr__(self, attrName):
		attr = Listener.__cbs.get(attrName)
		if attr is None:
			raise AttributeError("%s instance has no attribute '%s'." % (self.__class__.__name__, attrName))
		return attr


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def addListenCallback(self, name):
		"""
		添加一个监听回调
		"""
		if name not in Listener.__cbs:
			self.__cbs[name] = _Caller()


# ------------------------------------------------------------------------------
# global functions
# ------------------------------------------------------------------------------
def exit(exitCode):
	"""
	如果认为正常退出 exitCode 为 0，否则为其他值
	"""
	Listener().cbAppExit(exitCode)
	sys.exit(exitCode)
