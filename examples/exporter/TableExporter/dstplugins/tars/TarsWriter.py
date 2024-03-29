# -*- coding: utf-8 -*-
#

"""
写出字典

2018.03.07: writen by hyw
"""

import os
import re
import types
import string
from libs.custom_types.hlint import hlint
from libs.custom_types.xfloat import xfloat
from libs.custom_types.OrderDict import OrderDict
from libs.decorators import caller_in_dict
from TextEncoder import script2dst
from TextEncoder import script2sys
from TextEncoder import sys2script
from CustomTypes import CustomType
from config.CustomConfig import CustomConfig
from exporter.ExportExceptions import ExportFixException
from exporter.ExportWriter import ExportWriter
from TarsWidget import _TarsAttrTag
from TarsWidget import _TarsListValue

# --------------------------------------------------------------------
# inners
# --------------------------------------------------------------------
class _ErrorValueException(Exception):
	def __init__(self, value):
		self.value = value

class TarsWriter(ExportWriter):
	__escs = {
	'<': "&lt;",
	'>': "&gt;",
	'\t': "&#x09;",
	'\n': "&#x0a;",
	'\r': "&#x0d;",}
	chrs = []
	for ch in __escs:
		chrs.append("(%s)" % ch)
	__reptnESCs = re.compile("|".join(chrs))
	del chrs

	def __init__(self, exportTracer):
		ExportWriter.__init__(self, exportTracer)
		fileName = self.outInfo.dstFile
		path = os.path.split(fileName)[0]
		if not os.path.exists(script2sys(path)):
			raise ExportFixException("errSaveFilePath", path=path)
		try:
			self.__file = open(script2sys(fileName), "w")
		except Exception, err:
			raise ExportFixException("errSaveFileName", file=fileName, msg=sys2script(err.message))
		self.__encoding = self.outInfo.encoding
		self.__nl = CustomConfig().dstNewline


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __getTarsListValue(self, value):
		vstrs = []
		for e in value:
			vstr = self.__getTarsValue(e)
			if isinstance(vstr, basestring):
				vstrs.append(vstr)
			else:
				raise _ErrorValueException(e)
		return ", ".join(vstrs)

	def __getTarsValue(self, value):
		vtype = type(value)
		commonTypes = (int, long, hlint, float, xfloat)
		if vtype in commonTypes: return str(value)
		if vtype is bool: return str(value).lower()
		if vtype in (list, tuple, set):
			return self.__getTarsListValue(value)
		if isinstance(value, basestring):
			replacter = lambda m: self.__escs[m.group()]
			return self.__reptnESCs.sub(replacter, value)
		if isinstance(value, dict):
			return value
		if isinstance(value, _TarsListValue):
			return value
		return str(value)

	# -------------------------------------------------
	def __writeStartTag(self, writeTracer, tag):
		if isinstance(tag, _TarsAttrTag):
			attrs = []
			for attrName, value in tag.attrs.iteritems():
				vstr = self.__getTarsValue(value)
				attrs.append("%s=%s" % (attrName, vstr))
			vstrs = " ".join(attrs)
			if len(attrs): vstrs = " " + vstrs
			self.__file.write("<%s%s>" % (tag.tagName, vstrs))
		else:
			self.__file.write("<%s>" % tag)

	def __writeEndTag(self, writeTracer, tag):
		if isinstance(tag, _TarsAttrTag):
			self.__file.write(("</%s>" + self.__nl) % tag.tagName)
		else:
			self.__file.write(("</%s>" + self.__nl) % tag)

	# -------------------------------------------------
	def __writeDictItem(self, writeTracer, key, value):
		dnesting = writeTracer.dnesting
		self.__file.write("\t"*dnesting)

		tarsValue = self.__getTarsValue(value)
		if isinstance(tarsValue, basestring):
			self.__file.write("%s = %s%s" % (key, tarsValue, self.__nl))
		elif isinstance(tarsValue, dict):
			self.__writeStartTag(writeTracer, key)
			self.__file.write(self.__nl)
			self.__writeDict(writeTracer, tarsValue)
			self.__file.write("\t"*dnesting)
			self.__writeEndTag(writeTracer, key)
		elif isinstance(tarsValue, _TarsListValue):
			self.__writeStartTag(writeTracer, key)
			self.__file.write(self.__nl)
			for tag, v in tarsValue:
				self.__writeDict(writeTracer, {tag: v})
			self.__file.write("\t"*dnesting)
			self.__writeEndTag(writeTracer, key)

	def __writeDict(self, writeTracer, value):
		writeTracer.dnesting += 1						# 当前字典嵌套层数
		for k, v in value.iteritems():
			self.__writeDictItem(writeTracer, k, v)
		writeTracer.dnesting -= 1


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
		if tips != "": self.writeText(self.__nl + tips)
		self.writeText(("<%s>" + self.__nl) % outItemInfo.name)
		for index, (k, v) in enumerate(datas.iteritems()):
			writeTracer.dnesting = 1
			self.__writeDictItem(writeTracer, k, v)
			outItemTracer.writeTracer.onWritingOutItem(index)
		self.writeText(("</%s>" + self.__nl) % outItemInfo.name)
		outItemTracer.writeTracer.onEndWriteOutItem()
