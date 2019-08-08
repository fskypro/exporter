# -*- coding: utf-8 -*-
#

"""
写出字典

2011.09.20: writen by hyw
"""

import re
import types
from libs.custom_types.hlint import hlint
from libs.custom_types.xfloat import xfloat
from libs.custom_types.OrderDict import OrderDict
from libs.decorators import caller_in_dict
from TextEncoder import script2dst
from TextEncoder import sys2script
from config.CustomConfig import CustomConfig
from exporter.ExportExceptions import ExportFixException


# --------------------------------------------------------------------
# inners
# --------------------------------------------------------------------
class _ErrorValueException(Exception):
	def __init__(self, value):
		self.value = value


class JsonWriter:
	__typeWriters = {}

	def __init__(self, path, encoding="utf-8"):
		try:
			self.__file = open(script2sys(path), "w")
		except Exception, err:
			raise ExportFixException("errSaveFileName", file=path, msg=sys2script(err.message))
		self.__warps = 1
		self.__warp = 0
		self.__encoding = encoding
		self.__nl = CustomConfig().dstNewline

	def dispose(self):
		self.__file.close()

	# -----------------------------------------------------------------
	@caller_in_dict(__typeWriters, str, types.UnicodeType)
	def __writeStr(self, value):
		#value = re.sub(r'(?<=[^\\])"', r"\"", value)
		#value = re.sub("(?:\r\n)|\r|\n", r"\\n", value)
		value = value.replace("\\", "\\\\")
		self.writeText(script2dst(self.__encoding, "\"%s\"" % value))

	@caller_in_dict(__typeWriters, bool)
	def __writeBaseValue(self, value):
		self.__file.write("true" if value else "false")

	@caller_in_dict(__typeWriters, type(None))
	def __writeBaseValue(self, value):
		self.__file.write("null")

	@caller_in_dict(__typeWriters, int, long, hlint, float, xfloat)
	def __writeBaseValue(self, value):
		self.__file.write(str(value))

	@caller_in_dict(__typeWriters, tuple, list, set, frozenset)
	def _writeList(self, value):
		self.__file.write("[")
		maxIndex = len(value) - 1
		for idx, elem in enumerate(value):
			self.__writeValue(elem)
			if idx < maxIndex:
				self.__file.write(", ")
		self.__file.write("]")

	@caller_in_dict(__typeWriters, dict, OrderDict)
	def __writeDict(self, value):
		self.__warp += 1									# 当前字典嵌套层数
		dnesting = self.__warp
		isWarp = dnesting <= self.__warps					# 是否换行
		self.__file.write("{")
		maxIndex = len(value) - 1
		for idx, (k, v) in enumerate(value.iteritems()):
			if isWarp:
				self.__file.write(self.__nl +"\t"*dnesting)
				splitter = ","
			else:
				splitter = ", "
			self.__writeValue(k)
			self.__file.write(": ")
			self.__writeValue(v)
			if idx < maxIndex:
				self.__file.write(splitter)
		self.__file.write("}")

	def __writeValue(self, value):
		writer = self.__typeWriters.get(type(value))
		if writer is not None:
			writer(self, value)
		else:
			raise _ErrorValueException(value)

	# ----------------------------------------------------------------
	def writeText(self, text):
		self.__file.write(script2dst(self.__encoding, text))

	def write(self, datas, doc="", warps=1):
		self.__warps = warps
		count = len(datas)

		if doc != "": self.writeText(doc)
		maxIndex = len(datas) - 1
		self.__file.write(self.__nl + "{" + self.__nl)
		for idx, (key, value) in enumerate(datas.iteritems()):
			self.__warp = 1
			self.__file.write("\t")
			try:
				self.__writeValue(key)
				self.__file.write(": ")
				self.__writeValue(value)
			except _ErrorValueException, err:
				raise ExportFixException("errElemValue", key=key, value=str(err.value))
			if idx < maxIndex:
				self.__file.write("," + self.__nl)
			else:
				self.__file.write(self.__nl)
		self.__file.write("}" + self.__nl)
