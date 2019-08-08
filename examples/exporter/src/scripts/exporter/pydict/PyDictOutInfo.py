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
from PyDictWriter import PyDictWriter
from PyDictScanner import PyDictScanner
from config.CustomConfig import CustomConfig

_nl = CustomConfig().dstNewline

# --------------------------------------------------------------------
# 导出选项，每个选项对应一个导出配置中的数据字典。对应多个 DataSourceInfo
# attrs:
#    warps: 表示导出的配置字典中，前面几层嵌套会换行（最小值为 1）
#           如果不传入，则为 1
#    writers: 传入一组类型写出回调：{类型: 写出函数}
#        写出函数包含三个参数：writeTracer, value, fnStreamWriter
# --------------------------------------------------------------------
class PyDictOutItemInfo(OutItemInfo):
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
			self.__scanner = PyDictScanner(self)
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
			tips = "# export from: %s"
			tips = tips % ((_nl + "# and combines with: ").join(srcTexts))
			return tips + _nl
		return ""

	# -------------------------------------------------
	@property
	def warps(self):
		return max(1, self.queryExtraArg("warps", 1))

	@property
	def writers(self):
		return self.queryExtraArg("writers", {})


# --------------------------------------------------------------------
# 导出信息类，每个导出信息类对象对应一个导出配置
# attrs 是个可扩展参数，对应 config.xml 中的 outInfo 子标签，如：
#    beginCode      开始代码（导出配置的最开始写入一段代码）
#    endCode        结束代码（导出配置的最后写入的一段代码）
# --------------------------------------------------------------------
class PyDictOutInfo(OutInfo):
	__header = "# -*- coding: %(encoding)s -*-\n#\n".replace('\n', _nl)
	__record = '"""%(comment)s\nrecord:\n\texported by %(author)s.\n\tdate: %(date)s\n"""\n'.replace('\n', _nl)

	def __init__(self, dstFile, *outItemInfos, **attrs):
		self.__scanner = None
		self.__exportWriter = None
		OutInfo.__init__(self, dstFile, *outItemInfos, **attrs)
		self.beginCode = attrs.get("beginCode", "")					# 开始代码（在导出配置的最开始写入一段代码）
		self.endCode = attrs.get("endCode", "")						# 结束代码（在导出配置的最末端写入一段代码）


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def header(self):
		"""
		导出的配置头
		"""
		encodingText = PyDictOutInfo.__header % {"encoding": self.encoding}
		author = socket.gethostname()
		todate = date.today().strftime("%Y/%m/%d")
		if self.comment != "":
			comment = (_nl + "%s" + _nl) % self.comment
		else:
			comment = ""
		commentes = PyDictOutInfo.__record % {"comment": comment, "author": author, "date": todate}
		return encodingText + _nl + commentes

	# -------------------------------------------------
	@property
	def exportWriter(self):
		"""
		导出文件序列化器
		"""
		if self.__exportWriter is None:
			self.__exportWriter = PyDictWriter(self.exportTracer)
		return self.__exportWriter

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginWriteOut(self, outWriter):
		"""
		开始写出一个配置时调用
		outWriter.writeText(text)    : 在配置最顶头写入一串文本
		"""
		if self.beginCode != "":
			self.__writer.writeText(_nl + self.beginCode + _nl)

	def onWritenOut(self, outWriter):
		"""
		写出配置完毕后被调用
		outWriter.writeText(text)    : 在结束处写入一串文本
		"""
		if self.endCode != "":
			self.__writer.writeText(_nl + self.endCode + _nl)

	def onWriteClosed(self):
		"""
		写出配置成功并关闭后调用
		"""
		pass
