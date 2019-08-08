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
from ExportExceptions import ExportFixException


# --------------------------------------------------------------------
# 导出解释器，对应每一个 data_srcs/DataSource::iDataSource 的子类
# --------------------------------------------------------------------
class Scanner(object):
	def __init__(self, outItemInfo):
		self.__outItemInfo = outItemInfo
		self.__cbRowScanning = outItemInfo.onRowScanning

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def outItemInfo(self):
		return self.__outItemInfo

	@property
	def cbRowScanning(self):
		return self.__cbRowScanning


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRowScaned_(self, dsrcTracer, exp, row):
		"""
		对每一行翻译导出表达式
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def scan(self, expTracer):
		exp = expTracer.expInfo.exp
		expTracer.onBeginScanExpression()								# 开始扫描表达式关联的所有数据源
		for dsrcTracer in expTracer.scanDSrcTracers:
			dsrcTracer.onBeginScanDataSource()							# 开始扫描数据源
			count = dsrcTracer.dsrc.rowCount
			start = dsrcTracer.dsrc.startRow
			for row in xrange(start, count):
				self.onRowScaned_(dsrcTracer, exp, row)
				dsrcTracer.onScanningDataSource(row)					# 扫描数据源进度
			dsrcTracer.onEndScanDataSource()							# 结束扫描数据源
		expTracer.onEndScanExpression()									# 结束扫描表达式关联的所有数据源
