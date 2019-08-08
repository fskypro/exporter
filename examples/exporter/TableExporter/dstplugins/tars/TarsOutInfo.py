# -*- coding: utf-8 -*-
#

"""
实现 Tars 配置模板规范化类

writen by hyw -- 2018.03.07
"""

import time
import socket
from exporter.OutInfo import OutItemInfo
from exporter.OutInfo import OutInfo
from TarsWriter import TarsWriter
from TarsScanner import TarsScanner
from config.CustomConfig import CustomConfig

_nl = CustomConfig().dstNewline

# --------------------------------------------------------------------
# 导出选项，每个选项对应一个导出配置中的数据字典。对应多个 DataSourceInfo
# attrs:
#    writers: 传入一组类型写出回调：{类型: 写出函数}
#        写出函数包含三个参数：writeTracer, value, fnStreamWriter
# --------------------------------------------------------------------
class TarsOutItemInfo(OutItemInfo):
	"""
	从数据源中检索数据的导出选项
	"""
	def __init__(self, name, *expInfos, **attrs):
		OutItemInfo.__init__(self, name, *expInfos, **attrs)
		self.__scanner = None


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def scanner(self):
		if self.__scanner is None:
			self.__scanner = TarsScanner(self)
		return self.__scanner

	# -------------------------------------------------
	@property
	def srcTexts(self):
		srcTexts = []
		for expInfo in self.expInfos:
			for dsrc in expInfo.dsrcs:
				srcTexts.append(dsrc.getSrcText())
		return srcTexts

	@property
	def tips(self):
		"""
		导出配置中，在配置字典前的注释内容
		"""
		srcTexts = self.srcTexts
		if len(srcTexts):
			tips = "# export from:" + _nl
			tips += "#\t" + ((_nl + "#\t").join(srcTexts))
			return tips + _nl
		return ""

	@property
	def writers(self):
		return self.queryExtraArg("writers", {})


# --------------------------------------------------------------------
# 导出信息类，每个导出信息类对象对应一个导出配置
# attrs 是个可扩展参数，对应 config.xml 中的 outInfo 子标签，如：
#       servers: 指出有哪些服务器用到了该配置
# --------------------------------------------------------------------
class TarsOutInfo(OutInfo):
	__header = "# " + ('-' * 70) + _nl
	__header += "# description:" + _nl
	__header += "#\t%(comment)s" + _nl
	__header += "# for servers:" + _nl
	__header += "#\t%(servers)s" + _nl
	__header += "# record:" + _nl
	__header += "#\texported by %(author)s." + _nl
	__header += "#\texported time: %(dtime)s" + _nl
	__header += "# " + '-' * 70

	def __init__(self, dstFile, *outItemInfos, **attrs):
		self.__scanner = None
		self.__exportWriter = None
		self.__servers = attrs.get("servers", [])
		if isinstance(self.__servers, basestring):
			self.__servers = [self.__servers]
		OutInfo.__init__(self, dstFile, *outItemInfos, **attrs)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def header(self):
		"""
		导出的配置头
		"""
		author = socket.gethostname()
		dtime = time.strftime("%Y-%m-%d %H:%M:%S")
		commentes = TarsOutInfo.__header % {
			"comment": self.comment,
			"servers": "、".join(self.__servers) if len(self.__servers) else "unknow!",
			"author": author,
			"dtime": dtime}
		return commentes

	# -------------------------------------------------
	@property
	def exportWriter(self):
		"""
		导出文件序列化器
		"""
		if self.__exportWriter is None:
			self.__exportWriter = TarsWriter(self.exportTracer)
		return self.__exportWriter
