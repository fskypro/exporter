# -*- coding: utf-8 -*-
#

"""
实现一些给导出模板用的规范化类

writen by hyw -- 2014.04.15
"""

import time
import socket
from TableExporter import OrderDict
from config.CustomConfig import CustomConfig
from exporter.OutInfo import OutItemInfo
from exporter.OutInfo import OutInfo
from JsonWriter import JsonWriter
from JsonScanner import JsonScanner

_nl = CustomConfig().dstNewline

# ---------------------------------------------------------------------------------------
# 导出选项，每个选项对应一个导出配置中的数据字典。对应多个 DataSourceInfo
# attrs:
#    isWriteTips: 表示是否要写出导出配置数据源提示
#    warps: 表示导出的配置字典中，前面几层嵌套会换行（最小值为 1）
#           如果不传入，则为 1
#    writers: 传入一组类型写出回调：{类型: 写出函数}
#        写出函数包含三个参数：writeTracer, value, fnStreamWriter
# ---------------------------------------------------------------------------------------
class JsonOutItemInfo(OutItemInfo):
	"""
	从数据源中检索数据的导出选项
	"""
	def __init__(self, *expInfos, **attrs):
		OutItemInfo.__init__(self, "json", *expInfos, **attrs)
		self.__scanner = None
		self.__isWriteTips = attrs.get("isWriteTips", False)
		self.commentDoc = {}

	# ----------------------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------------------
	@property
	def scanner(self):
		if self.__scanner is None:
			self.__scanner = JsonScanner(self)
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
			tips = "// export from: %s"
			tips = tips % ((_nl + "// and combines with: ").join(srcTexts))
			return tips + _nl
		return ""

	@property
	def isWriteTips(self):
		"""
		是否要写出导出配置数据源提示
		"""
		return self.__isWriteTips

	# -------------------------------------------------
	@property
	def warps(self):
		return max(1, self.queryExtraArg("warps", 1))

	@property
	def writers(self):
		return self.queryExtraArg("writers", {})

	# ----------------------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------------------
	def onAllScanned(self, datas):
		"""
		全部扫描完毕后被调用
		@type			datas: OrderDict
		"""
		OutItemInfo.onAllScanned(self, datas)
		if len(self.commentDoc) > 0:
			datas.insert(0, self.commentDoc.items()[0])


# ---------------------------------------------------------------------------------------
# 导出信息类，每个导出信息类对象对应一个导出配置
# attrs:
#     commentKey: 注释键
# ---------------------------------------------------------------------------------------
class JsonOutInfo(OutInfo):
	__header = "// " + ('-' * 70) + _nl
	__header += "// description:" + _nl
	__header += "//\t%(description)s" + _nl
	__header += "// for servers:" + _nl
	__header += "//\t%(servers)s" + _nl
	__header += "// record:" + _nl
	__header += "//\texported by %(author)s." + _nl
	__header += "//\texported time: %(dtime)s" + _nl
	__header += "// " + '-' * 70

	def __init__(self, dstFile, *outItemInfos, **attrs):
		self.__scanner = None
		self.__exportWriter = None
		self.__servers = attrs.get("servers", [])
		if isinstance(self.__servers, basestring):
			self.__servers = [self.__servers]
		attrs["isWriteHeader"] = attrs.get("isWriteHeader", False)			# 默认不写头（标准 json 不支持注释，所以标准 json 不能写头）
		OutInfo.__init__(self, dstFile, *outItemInfos, **attrs)

		# 判断是否需要些注释
		if attrs.has_key("commentKey"):
			for outItemInfo in outItemInfos:
				outItemInfo.commentDoc[attrs["commentKey"]] = self.__getCommentDoc()

	# ----------------------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------------------
	@property
	def header(self):
		"""
		导出的配置头
		"""
		author = socket.gethostname()
		dtime = time.strftime("%Y-%m-%d %H:%M:%S")
		return JsonOutInfo.__header % self.__getCommentDoc()

	# -------------------------------------------------
	@property
	def exportWriter(self):
		"""
		导出文件序列化器
		"""
		if self.__exportWriter is None:
			self.__exportWriter = JsonWriter(self.exportTracer)
		return self.__exportWriter

	# ----------------------------------------------------------------------------
	# private
	# ----------------------------------------------------------------------------
	def __getCommentDoc(self):
		author = socket.gethostname()
		dtime = time.strftime("%Y-%m-%d %H:%M:%S")
		return OrderDict([
			("description", self.comment),
			("servers", "、".join(self.__servers) if len(self.__servers) else "unknow!"),
			("author", author),
			("dtime", dtime),
		])

	# ----------------------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------------------
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
