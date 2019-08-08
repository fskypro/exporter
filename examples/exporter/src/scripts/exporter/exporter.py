# -*- coding: utf-8 -*-
#

"""
2011.09.20: writen by hyw
"""

from engine import Listener
from config.CustomConfig import CustomConfig
from ExportExceptions import ExportFixException


# --------------------------------------------------------------------
# 配置选项导出器，对应一个导出配置选项（导出表达式）：exporter.OutInfo::PyDictOutItemInfo
# --------------------------------------------------------------------
class OutItemExporter(object):
	def __init__(self, exportItemTracer):
		self.__exportItemTracer = exportItemTracer
		self.__outItemInfo = exportItemTracer.outItemInfo
		self.__scanner = self.__outItemInfo.scanner

	def export(self, writer):
		"""
		扫描一个导出表达式涉及到的所有数据源
		"""
		exportItemTracer = self.__exportItemTracer
		outItemInfo = exportItemTracer.outItemInfo
		exportItemTracer.onBeginExportConfigItem()						# 开始导出一个字典
		for scanExpTracer in exportItemTracer.scanExpTracers:				# 开始扫描一个字典相关的所有数据源
			self.__scanner.scan(scanExpTracer)
		outItemInfo.onAllScanned(self.__exportItemTracer.datas)			# 所有该字典相关的数据扫描完毕

		if writer and type(outItemInfo.name) is str:
			outItemInfo.onBeginWriteOut(writer)								# 开始对一个字典写出配置
			writer.writeOutItem(exportItemTracer)							# 对该字典写出配置
			outItemInfo.onWritenOut(writer)									# 结束该字典的写出配置操作
		exportItemTracer.onEndExportConfigItem()							# 结束导出一个字典


# --------------------------------------------------------------------
# 配置导出器，对应一个导出配置：exporter.OutInfo::PyDictOutInfo
# --------------------------------------------------------------------
class OutExporter(object):
	def __init__(self, outInfo):
		self.__outInfo = outInfo
		if isinstance(outInfo.dstFile, basestring):
			self.__writer = outInfo.exportWriter
			if outInfo.isWriteHeader:
				self.__writer.writeText(outInfo.header)
				self.__writer.writeText(CustomConfig().dstNewline)
			outInfo.onBeginWriteOut(self.__writer)
		else:
			self.__writer = None


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def run(self):
		writer = self.__writer
		exportTracer = self.__outInfo.exportTracer
		exportTracer.onBeginExportConfig()
		count = len(exportTracer.exportItemTracers)
		for exportItemTracer in exportTracer.exportItemTracers:
			OutItemExporter(exportItemTracer).export(writer)
			count = count - 1
			if count > 0 and writer:
				writer.writeText(CustomConfig().dstNewline)
		if writer:
			self.__outInfo.onWritenOut(writer)
			writer.close()
			self.__outInfo.onWriteClosed()
		exportTracer.onEndExportConfig()


# --------------------------------------------------------------------
# global functions
# --------------------------------------------------------------------
def export(tplModule):
	"""
	导出
	"""
	outInfos = getattr(tplModule, "outInfos", None)
	if outInfos is None:
		outInfo = getattr(tplModule, "outInfo", None)
		if outInfo is None:
			raise ExportFixException("errNoConfigInfo", outInfo="outInfo", outInfos = "outInfos")
		else:
			outInfos = [outInfo]

	Listener().cbBeginExport(tplModule)					# 准备导出
	for outInfo in outInfos:								# 每个 outInfo 对应一个导出的配置文件
		OutExporter(outInfo).run()						# 准备导出其中一个配置
	Listener().cbEndExport(tplModule)					# 结束导出
