# -*- coding: utf-8 -*-
#

"""
写出字典

2011.09.20: writen by hyw
"""

import re
import types
import string
from libs.custom_types.hlint import hlint
from libs.custom_types.xfloat import xfloat
from libs.custom_types.OrderDict import OrderDict
from libs.decorators import caller_in_dict
from TextEncoder import script2dst
from TextEncoder import sys2script
from CustomTypes import CustomType
from config.CustomConfig import CustomConfig
from ..ExportExceptions import ExportFixException
from ..ExportWriter import ExportWriter

# --------------------------------------------------------------------
# inners
# --------------------------------------------------------------------
class _ErrorValueException(Exception):
	def __init__(self, value):
		self.value = value

class PyDictWriter(ExportWriter):
	__typeWriters = {}

	def __init__(self, exportTracer):
		ExportWriter.__init__(self, exportTracer)
		fileName = self.outInfo.dstFile
		try:
			self.__file = open(script2sys(fileName), "w")
		except Exception, err:
			raise ExportFixException("errSaveFileName", file=fileName, msg=sys2script(err.message))
		self.__encoding = self.outInfo.encoding
		self.__nl = CustomConfig().dstNewline


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@caller_in_dict(__typeWriters, str, types.UnicodeType)
	def __writeStr(self, writeTracer, value):
		value = re.sub(r'(?<=[^\\])"', r"\"", value)
		value = re.sub("(?:\r\n)|\r|\n", self.__nl, value)
		self.writeText("\"%s\"" % value)

	@caller_in_dict(__typeWriters, int, long, hlint, float, xfloat, bool, type(None))
	def __writeBaseValue(self, writeTracer, value):
		self.__file.write(str(value))

	@caller_in_dict(__typeWriters, tuple)
	def _writeTuple(self, writeTracer, value):
		self.__file.write("(")
		maxIndex = max(1, len(value) - 1)
		for idx, elem in enumerate(value):
			self.__writeValue(writeTracer, elem)
			if idx < maxIndex:
				self.__file.write(", ")
		self.__file.write(")")

	@caller_in_dict(__typeWriters, list)
	def _writeList(self, writeTracer, value):
		self.__file.write("[")
		maxIndex = len(value) - 1
		for idx, elem in enumerate(value):
			self.__writeValue(writeTracer, elem)
			if idx < maxIndex:
				self.__file.write(", ")
		self.__file.write("]")

	@caller_in_dict(__typeWriters, dict, OrderDict)
	def __writeDict(self, writeTracer, value):
		writeTracer.dnesting += 1									# 当前字典嵌套层数
		dnesting = writeTracer.dnesting
		isWarp = dnesting <= writeTracer.outItemInfo.warps			# 是否换行
		self.__file.write("{")
		maxIndex = len(value) - 1
		for idx, (k, v) in enumerate(value.iteritems()):
			if isWarp:
				self.__file.write(self.__nl + "\t"*dnesting)
				splitter = ","
			else:
				splitter = ", "
			self.__writeValue(writeTracer, k)
			self.__file.write(": ")
			self.__writeValue(writeTracer, v)
			if idx < maxIndex:
				self.__file.write(splitter)
		self.__file.write("}")

	@caller_in_dict(__typeWriters, set)
	def __writeSet(self, writeTracer, value):
		self.__file.write("set([")
		for elem in value:
			self.__writeValue(writeTracer, elem)
			self.__file.write(", ")
		self.__file.write("])")

	@caller_in_dict(__typeWriters, frozenset)
	def __writeFrozenset(self, writeTracer, value):
		self.__file.write("frozenset([")
		for elem in value:
			self.__writeValue(writeTracer, elem)
			self.__file.write(", ")
		self.__file.write("])")

	def __writeValue(self, writeTracer, value):
		valueType = type(value)
		writer = writeTracer.writers.get(valueType)
		if writer is not None:
			writer(writeTracer, value)
		else:
			writer = self.__typeWriters.get(valueType)
			if writer is not None:
				writer(self, writeTracer, value)
			elif isinstance(value, CustomType):
				self.__file.write("%r" % value)
			else:
				raise _ErrorValueException(value)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def close(self):
		try:
			self.__file.close()
			self.__file = None
		except:
			pass

	def writeText(self, text):
		"""
		允许写出一段文本
		"""
		self.__file.write(script2dst(self.__encoding, text))

	def writeOutItem(self, outItemTracer):
		"""
		写入不同类型的值
		"""
		datas = outItemTracer.datas
		count = len(datas)

		outItemInfo = outItemTracer.outItemInfo
		writeTracer = outItemTracer.writeTracer
		writeTracer.onBeginWriteConfigItem()
		tips = outItemInfo.tips
		warps = outItemInfo.warps								# 前面的几层嵌套换行
		if tips != "": self.writeText(self.__nl + tips)
		self.__file.write((self.__nl + "%s = {" + self.__nl) % outItemInfo.name)
		for idx, (key, value) in enumerate(datas.iteritems()):
			writeTracer.dnesting = 1
			self.__file.write("\t")
			try:
				self.__writeValue(writeTracer, key)
				self.__file.write(": ")
				self.__writeValue(writeTracer, value)
			except _ErrorValueException, err:
				raise ExportFixException("errElemValue", key=key, value=str(err.value))
			self.__file.write("," + self.__nl)
			outItemTracer.writeTracer.onWritingOutItem(idx)
		self.__file.write("\t}" + self.__nl)
		outItemTracer.writeTracer.onEndWriteOutItem()
