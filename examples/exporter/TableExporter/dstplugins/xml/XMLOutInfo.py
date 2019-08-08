# -*- coding: utf-8 -*-
#

"""
实现一些给导出模板用的规范化类

writen by hyw -- 2013.04.09
"""

import socket
from datetime import date
from ..OutInfo import OutItemInfo
from ..OutInfo import OutInfo
from XMLWriter import XMLWriter
from XMLScanner import XMLScanner
from config.CustomConfig import CustomConfig

_nl = CustomConfig().dstNewline

# --------------------------------------------------------------------
# 导出选项，每个选项对应一个导出配置中的数据字典。对应多个 DataSourceInfo
# attrs:
#    writers: 传入一组类型写出回调：{类型: 写出函数}
#        写出函数包含三个参数：writeTracer, value, fnStreamWriter
# --------------------------------------------------------------------
class XMLOutItemInfo(OutItemInfo):
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
			self.__scanner = XMLScanner(self)
		return self.__scanner

	# -------------------------------------------------
	@property
	def tips(self):
		"""
		导出配置中，在配置字典前的注释内容
		"""
		srcTexts = []
		for expInfo in self.expInfos:
			for dsrc in expInfo.dsrcs:
				srcTexts.append(dsrc.getSrcText())
		if len(srcTexts):
			tips = "<!-- export from: %s -->"
			tips = tips % ((_nl + "# and combines with: ").join(srcTexts))
			return tips + _nl
		return ""

	@property
	def writers(self):
		return self.queryExtraArg("writers", {})


# --------------------------------------------------------------------
# 导出信息类，每个导出信息类对象对应一个导出配置
# attrs 是个可扩展参数，对应 config.xml 中的 outInfo 子标签，如：
# --------------------------------------------------------------------
class XMLOutInfo(OutInfo):
	__header = '<?xml version="1.0" encoding="%(encoding)s"?>'
	__record = '<!-- %(comment)s\nrecord:\n\texported by %(author)s.\n\tdate: %(date)s\n-->\n'.replace('\n', _nl)

	def __init__(self, dstFile, *outItemInfos, **attrs):
		self.__scanner = None
		self.__exportWriter = None
		OutInfo.__init__(self, dstFile, *outItemInfos, **attrs)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def header(self):
		"""
		导出的配置头
		"""
		encodingText = XMLOutInfo.__header % {"encoding": self.encoding}
		author = socket.gethostname()
		todate = date.today().strftime("%Y/%m/%d")
		if self.comment != "":
			comment = _nl + self.comment + _nl
		else:
			comment = ""
		commentes = XMLOutInfo.__record % {"comment": comment, "author": author, "date": todate}
		return encodingText + _nl + commentes

	# -------------------------------------------------
	@property
	def exportWriter(self):
		"""
		导出文件序列化器
		"""
		if self.__exportWriter is None:
			self.__exportWriter = XMLWriter(self.exportTracer)
		return self.__exportWriter
