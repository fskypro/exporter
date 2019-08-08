# -*- coding: utf-8 -*-
#

"""
对应 config.xml 配置

2011.09.20: writen by hyw
"""


from libs import Path
from libs.Singleton import Singleton
from TextEncoder import script2sys
from libs.SimpleXML import SimpleXML
from libs.custom_types.hlint import hlint
from libs.custom_types.Vectors import Vector2
from libs.custom_types.Vectors import Vector3
from libs.custom_types.Vectors import Vector4
from TextEncoder import script2sys, sys2script
from ConfigExceptions import ConfigFixException
from ConfigExceptions import ConfigTagPathException
from ConfigExceptions import ConfigTagValueException


_xmlReaders = {
	str: "asString",
	int: "asInt",
	long: "asInt",
	hlint: "asHLInt",
	float: "asFloat",
	bool: "asBool",
	Vector2: "asVector2",
	Vector3: "asVector3",
	Vector4: "asVector4",
	}

_xmlArrayReaders = {
	(str,): "readStrings",
	(int,): "readInts",
	(long,): "readInts",
	(hlint,): "readHLInts",
	(float,): "readFloats",
	(bool,): "readBools",
	(Vector2,): "readVector2s",
	(Vector3,): "readVector3s",
	(Vector4,): "readVector4s",
	}


# --------------------------------------------------------------------
# custom config
# --------------------------------------------------------------------
class CustomConfig(Singleton):
	def __init__(self):
		self.__init()
		self.__tlpRoots = None
		self.__srcRoots = None
		self.__dstRoot = None
		self.__valueCaches = {}


	# ---------------------------------------------------------------------
	# private
	# ---------------------------------------------------------------------
	def __init(self):
		xml = SimpleXML(Path.executeDirectory())
		cfgSect = xml.openSection("config.xml")
		if cfgSect is None:
			raise ConfigFixException("errNoConfig", file="config.xml")
		self.__cfgSect = cfgSect

	@staticmethod
	def __getFullPath(rpath):
		path = Path.realToExecutePath(rpath)
		return sys2script(path)

	# ---------------------------------------------------------------------
	# properties
	# ---------------------------------------------------------------------
	@property
	def tplRoots(self):
		"""
		模板文件路径列表
		"""
		if self.__tlpRoots is None:
			self.__tlpRoots = []
			try:
				roots = self.__cfgSect["paths"]["tplRoots"].readStrings("item")
			except:
				raise ConfigTagPathException("<paths>/<tplRoots>")
			for root in roots:
				self.__tlpRoots.append(Path.realToExecutePath(root))
		return self.__tlpRoots

	@property
	def syscodeTplRoots(self):
		roots = []
		for root in self.tplRoots:
			roots.append(script2sys(root))
		return roots

	# ----------------------------------------------
	@property
	def syscodeSrcPluginRoot(self):
		"""
		数据源插件（相对可执行文件的路径）
		"""
		root = self.__cfgSect["paths"].readString("srcPluginRoot")
		return script2sys(Path.realToExecutePath(root))

	@property
	def syscodeDstPluginRoot(self):
		root = self.__cfgSect["paths"].readString("dstPluginRoot")
		return script2sys(Path.realToExecutePath(root))

	# ----------------------------------------------
	@property
	def srcRoots(self):
		"""
		excel 文件的根路径列表
		"""
		if self.__srcRoots is None:
			self.__srcRoots = []
			try:
				roots = self.__cfgSect["paths"]["srcRoots"].readStrings("item")
			except:
				raise ConfigTagPathException("<paths>/<srcRoots>")
			for root in roots:
				self.__srcRoots.append(Path.realToExecutePath(root))
		return self.__srcRoots

	@property
	def syscodeSrcRoots(self):
		roots = []
		for root in self.srcRoots:
			roots.append(root)
		return roots

	# ----------------------------------------------
	@property
	def dstRoot(self):
		"""
		导出路径的根目录
		"""
		if self.__dstRoot is None:
			try:
				root = self.__cfgSect["paths"].readString("dstRoot")
			except:
				raise ConfigTagPathException("<paths>/<dstRoot>")
			self.__dstRoot = Path.realToExecutePath(root)
		return self.__dstRoot

	@property
	def syscodeDstRoot(self):
		return script2sys(dstRoot)

	# ------------------------------------------------------------------
	@property
	def dstEncoding(self):
		"""
		导出配置的编码方式
		"""
		encoding = self.__cfgSect["outInfo"].readString("dstEncoding").lower()
		if encoding == "":
			raise ConfigTagValueException("<outInfo>/<dstEncoding>")
		return encoding

	@property
	def dstNewline(self):
		"""
		导出配置中的换行符
		"""
		newline = self.__cfgSect["outInfo"].readString("dstNewline")
		if newline == "\\r\\n":
			return "\r\n"
		elif newline == "\\n":
			return "\n"
		else:
			raise ConfigTagValueException("<outInfo>/<dstNewline>")

	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def query(self, path, vtype=str):
		"""
		读取 config 配置中的一个标签值，嵌套标签用“/”分隔
		"""
		key = (path, vtype)
		value = self.__valueCaches.get(key)
		if value is not None: return value
		_xmlReader = _xmlReaders.get(vtype)
		if _xmlReader is not None:
			try:
				value = getattr(self.__cfgSect[path], _xmlReader)
			except:
				raise ConfigTagPathException("<%s>" % path.replace("/", ">/<"))
		else:
			_xmlReader = _xmlArrayReaders.get(vtype)
			if _xmlReader is None:
				raise ConfigTagValueException("<%s>" % path.replace("/", ">/<"))
			try:
				value = getattr(self.__cfgSect[path], _xmlReader)("item")
			except:
				raise ConfigTagPathException("<%s>" % path.replace("/", ">/<"))
		self.__valueCaches[key] = value
		return value
