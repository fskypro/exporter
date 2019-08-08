# -*- coding: utf-8 -*-
#

"""
实现一些给导出模板用的规范化类

writen by hyw -- 2014.03.18
"""

import os
import weakref
from abc import ABCMeta
from abc import abstractproperty
from libs import Path
from libs.custom_types.OrderDict import OrderDict
from config.CustomConfig import CustomConfig
from ExportTracers import ExportTracer

# --------------------------------------------------------------------
# 表达式信息，一个表达式可能关联两个以上的表头一样的数据源
# --------------------------------------------------------------------
class ExpInfo(object):
	def __init__(self, exp, *dsrcs):
		self.__exp = exp
		self.__dsrcs = dsrcs


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def exp(self):
		return self.__exp

	@property
	def dsrcs(self):
		return self.__dsrcs

	@property
	def rowCount(self):
		return sum(dsrc.rowCount for dsrc in self.__dsrcs)

	@property
	def loadTime(self):
		return sum(dsrc.loadTime for dsrc in self.__dsrcs)


# --------------------------------------------------------------------
# 导出选项，每个选项对应一个导出配置中的数据字典。对应多个 DataSourceInfo
# --------------------------------------------------------------------
class OutItemInfo(object):
	__metaclass__ = ABCMeta

	class __INNER: pass

	def __init__(self, name, *expInfos, **attrs):
		self.__name = name							# 名称可以为 None，如果为 None，则该字典不会写出到配置
		self.__datas = OrderDict()						# 要导出的最终数据字典
		self.__expInfos = expInfos						# 数据源信息
		self.__attrs = attrs


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@abstractproperty
	def scanner(self):
		return None

	# -------------------------------------------------
	@property
	def name(self):
		"""
		导出配置中的字典名称
		"""
		return self.__name

	@property
	def datas(self):
		"""
		导出配置的数据（扫描完毕后才有用，否则为空）
		"""
		return self.__datas

	@property
	def expInfos(self):
		"""
		所有的表达式信息
		"""
		return self.__expInfos

	# -------------------------------------------------
	@property
	def dsrcTextList(self):
		"""
		返回一组字符串，以表示整个导出字典数据源来源
		"""
		srcTexts = []
		for expInfo in self.expInfos:
			for dsrc in expInfo.dsrcs:
				srcTexts.append(dsrc.getSrcText())
		return srcTexts

	# -------------------------------------------------
	@property
	def rowCount(self):
		return sum(ei.rowCount for ei in self.expInfos)

	@property
	def loadTime(self):
		return sum(ei.loadTime for ei in self.expInfos)


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onRowScanning(self, datas, key, value, row, dsrc):
		"""
		每解释一行时被调用，还没添加进 datas
		@param			datas: 整个数据表
		@param			key  : 当前解释到的行的 key
		@param			value: 当前行数据值
		@param			row  : 当前解释到的行索引
		@param			dsrc : 当前行所在数据源信息
		@return			     : None/KEYRET_NORMAL/KEYRET_EMPTY/KEYRET_IGNOR
						       None 正常导出
						       KEYRET_NORMAL 不导出并且不提示
						       KEYRET_EMPTY 认为空行提示
						       KEYRET_IGNOR 认为该行忽略并提示
		"""
		return None

	def onAllScanned(self, datas):
		"""
		全部扫描完毕后被调用
		@type			datas: OrderDict
		"""
		pass

	def onBeginWriteOut(self, outWriter):
		"""
		准备写出配置前被调用
		outWriter.writeText(text)    : 写入一串文本
		"""
		pass

	def onWritenOut(self, outWriter):
		"""
		写出配置完毕后被调用
		outWriter.writeText(text)    : 写入一串文本
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def queryExtraArg(self, key, defValue=__INNER):
		if defValue is self.__INNER:
			return self.__attrs[key]
		return self.__attrs.get(key, defValue)


# --------------------------------------------------------------------
# 导出信息类，每个导出信息类对象对应一个导出配置
# attrs 是个可扩展参数，对应 config.xml 中的 outInfo 子标签，如：
#    dstEncoding    目标文件的编码
#    comment          导出文件注释
#    isWriteHeader 是否写头
# --------------------------------------------------------------------
class OutInfo(object):
	__metaclass__ = ABCMeta

	class __INNER: pass

	def __init__(self, dstFile, *outItemInfos, **attrs):
		"""
		dstFile 允许为 None，如果为 None，则只解释表格，不将表格导出到配置文件
		"""
		self.__attrs = attrs
		self.__exportTracer = None										# 导出信息追踪器（实现将导出过程反馈给 UI）
		self.__dstFile = dstFile												# 导出文件（可以传入 None，如果传入 None，将不写出文件）
		self.__outItemInfos = outItemInfos								# 导出字典列表
		self.__encoding = attrs.get("dstEncoding", \
			CustomConfig().query("outInfo/dstEncoding", str))
		self.__isWriteHeader = attrs.get("isWriteHeader", True)			# 写出配置中，是否有注释头
		self.comment = attrs.get("comment", "")							# 导出模块的注释


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def exportTracer(self):
		if self.__exportTracer is None:
			self.__exportTracer = ExportTracer(self)
		return self.__exportTracer

	@abstractproperty
	def exportWriter(self):
		"""
		导出文件序列化器
		"""
		return None

	# -------------------------------------------------
	@property
	def loadTime(self):
		"""
		加载所有数据源的时间
		"""
		loadTime = 0
		for exportItem in self.outItemInfos:
			loadTime += exportItem.loadTime
		return loadTime

	@property
	def encoding(self):
		"""
		导出配置编码
		"""
		return self.__encoding

	# -------------------------------------------------
	@property
	def dstFile(self):
		"""
		导出文件路径
		"""
		if self.__dstFile is None: return None
		path = os.path.join(CustomConfig().dstRoot, self.__dstFile)
		return Path.normalizePath(path)

	@property
	def outItemInfos(self):
		"""
		导出到同一个配置文件的所有配置选项
		"""
		return self.__outItemInfos

	# -------------------------------------------------
	@property
	def isWriteHeader(self):
		"""
		是否要写出注释头
		"""
		return self.__isWriteHeader

	@property
	def header(self):
		return ""

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginWriteOut(self, outWriter):
		"""
		开始写出一个配置时调用
		outWriter.writeText(text)    : 在配置最顶头写入一串文本
		"""
		pass

	def onWritenOut(self, outWriter):
		"""
		写出配置完毕后被调用
		outWriter.writeText(text)    : 在结束处写入一串文本
		"""
		pass

	def onWriteClosed(self):
		"""
		写出配置成功并关闭后调用
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def queryExtraArg(self, key, defValue=__INNER):
		if defValue is self.__INNER:
			return self.__attrs[key]
		return self.__attrs.get(key, defValue)
