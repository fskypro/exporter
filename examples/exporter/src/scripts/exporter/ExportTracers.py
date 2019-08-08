# -*- coding: utf-8 -*-
#

"""
导出跟踪类

2011.09.20: writen by hyw
"""

import time
import weakref
from engine import Listener
from libs.custom_types.OrderDict import OrderDict


class BaseTracer(object):
	def __init__(self, owner=None):
		if owner is not None:
			self.__owner = weakref.ref(owner)
		self.__startTime = 0
		self.__wasteTime = 0.0						# 导出时间


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def owner(self):
		if self.__owner is None:
			return None
		return self.__owner()

	@property
	def wasteTime(self):
		return self.__wasteTime


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginTrace_(self):
		self.__startTime = time.time()

	def onEndTrace_(self):
		self.__wasteTime = time.time() - self.__startTime


# --------------------------------------------------------------------
# 扫描一个数据源的跟踪信息，对应 data_srcs/DataSource::iDataSource 的子类
# --------------------------------------------------------------------
class ScanDataSourceTracer(BaseTracer):
	def __init__(self, owner, dsrc):
		BaseTracer.__init__(self, owner)
		self.dsrc = dsrc

		self.emptyRows = []							# 空行列表：{数据源: [空行索引列表]}
		self.ignorRows = []							# 被忽略的键列表：{数据源: [忽略的行索引列表]}


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def datas(self):
		return self.owner.datas

	@property
	def dbKeys(self):
		return self.owner.dbKeys

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginScanDataSource(self):
		Listener().cbBeginScanDataSource(self)
		Listener().cbScanningDataSource(self, 0)

	def onScanningDataSource(self, row):
		Listener().cbScanningDataSource(self, row)

	def onEndScanDataSource(self):
		Listener().cbEndScanDataSource(self)


# --------------------------------------------------------------------
# 扫描一个导出表达式的跟踪信息，对应 ExportInfo.ExpInfo
# --------------------------------------------------------------------
class ScanExpTracer(BaseTracer):
	def __init__(self, owner, expInfo):
		BaseTracer.__init__(self, owner)
		self.expInfo = expInfo
		self.scanDSrcTracers = []
		for dsrc in expInfo.dsrcs:
			tracer = ScanDataSourceTracer(self, dsrc)
			self.scanDSrcTracers.append(tracer)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def datas(self):
		return self.owner.datas

	@property
	def dbKeys(self):
		return self.owner.dbKeys


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginScanExpression(self):
		BaseTracer.onBeginTrace_(self)

	def onEndScanExpression(self):
		BaseTracer.onEndTrace_(self)


# --------------------------------------------------------------------
# 写出配置选项跟踪信息
# --------------------------------------------------------------------
class WriteItemTracer(BaseTracer):
	def __init__(self, owner):
		BaseTracer.__init__(self, owner)
		self.writers = self.owner.outItemInfo.writers
		self.dnesting = 1


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def datas(self):
		return self.owner.datas

	@property
	def outItemInfo(self):
		return self.owner.outItemInfo


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginWriteConfigItem(self):
		BaseTracer.onBeginTrace_(self)
		Listener().cbBeginWriteOutItemInfo(self)
		Listener().cbWritingOutItemInfo(self, 0)

	def onWritingOutItem(self, index):
		Listener().cbWritingOutItemInfo(self, index)

	def onEndWriteOutItem(self):
		BaseTracer.onEndTrace_(self)
		Listener().cbEndWriteOutItemInfo(self)


# --------------------------------------------------------------------
# 扫描一个配置选项的跟踪信息，对应 ExportInfo::PyDictOutItemInfo
# --------------------------------------------------------------------
class ExportItemTracer(BaseTracer):
	def __init__(self, owner, outItemInfo):
		BaseTracer.__init__(self, owner)
		self.outItemInfo = outItemInfo
		self.scanExpTracers = []
		for expInfo in outItemInfo.expInfos:
			tracer = ScanExpTracer(self, expInfo)
			self.scanExpTracers.append(tracer)
		self.__dbKeys = {}									# 重复键数：{重复的键值: 重复数量}
		self.writeTracer = WriteItemTracer(self)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def datas(self):
		return self.outItemInfo.datas

	@property
	def dbKeys(self):
		return self.__dbKeys

	# -------------------------------------------------
	@property
	def loadDSrcsTime(self):
		return self.outItemInfo.loadTime

	@property
	def scanDSrcsTime(self):
		return sum(expTracer.wasteTime for expTracer in self.scanExpTracers)

	@property
	def writeTime(self):
		return self.writeTracer.wasteTime

	# -------------------------------------------------
	@property
	def emptyCount(self):
		count = 0
		for expTracer in self.scanExpTracers:
			for dsrcTracer in expTracer.scanDSrcTracers:
				count += len(dsrcTracer.emptyRows)
		return count

	@property
	def ignorCount(self):
		count = 0
		for expTracer in self.scanExpTracers:
			for dsrcTracer in expTracer.scanDSrcTracers:
				count += len(dsrcTracer.ignorRows)
		return count


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginExportConfigItem(self):
		BaseTracer.onBeginTrace_(self)
		Listener().cbBeginExportOutItemInfo(self)

	def onEndExportConfigItem(self):
		BaseTracer.onEndTrace_(self)
		Listener().cbEndExportOutItemInfo(self)


# --------------------------------------------------------------------
# 导出一个配置的跟踪信息，对应 ExportInfo::PyDictOutInfo
# --------------------------------------------------------------------
class ExportTracer(BaseTracer):
	def __init__(self, outInfo):
		BaseTracer.__init__(self)
		self.outInfo = outInfo											# 导出配置信息
		self.exportItemTracers = []									# 扫描导出表达式临时信息
		for outItemInfo in outInfo.outItemInfos:
			tracer = ExportItemTracer(self, outItemInfo)
			self.exportItemTracers.append(tracer)


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginExportConfig(self):
		BaseTracer.onBeginTrace_(self)
		Listener().cbBeginExportOutInfo(self)

	def onEndExportConfig(self):
		BaseTracer.onEndTrace_(self)
		Listener().cbEndExportOutInfo(self)
