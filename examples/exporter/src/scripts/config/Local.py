# -*- coding: utf-8 -*-
#

"""
语言配置

2011.09.20: writen by hyw
"""

from libs import Path
from libs.SimpleXML import SimpleXML
from libs.Singleton import Singleton
from Exceptions import BaseException
from SysConfig import SysConfig


class Local(Singleton):
	def __init__(self):
		xml = SimpleXML(Path.executeDirectory())
		try:
			self.__lngSect = xml.openSection(SysConfig().lngFile)
		except Exception, err:
			raise err
		if self.__lngSect is None:
			raise BaseException("Error", "config file 'bin.xml' is not exist.")


	# ---------------------------------------------------------------------
	# public
	# ---------------------------------------------------------------------
	def getLocalText(self, scope, tag):
		"""
		获取指定语言版本文本，不做编码转换，args 必须与 python 脚本编码一致
		"""
		sect = self.__lngSect[scope]
		if sect is None or sect[tag] is None or \
			sect[tag].asString is None:
				raise BaseException("Error", "language file is not contain the tag '<%s>/<%s>'." % (scope, tag))
		return sect[tag].asString

	def formatLocalText(self, _scope, _tag, **args):
		"""
		格式化指定语言版本文本，不做编码转换，args 必须与 python 脚本编码一致
		"""
		sect = self.__lngSect[_scope]
		if sect is None or sect[_tag] is None or \
			sect[_tag].asString is None:
				raise BaseException("Error", "language file is not contain the tag '<%s>/<%s>'." % (_scope, _tag))
		text = sect[_tag].asString
		try:
			text = text % args
		except TypeError:
			raise BaseException("Error", "format message in tag '<%s>/<%s>' in language file fial: (args='%s')" % (_scope, _tag, args))
		return text
