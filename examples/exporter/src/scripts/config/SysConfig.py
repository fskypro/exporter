# -*- coding: utf-8 -*-
#

"""
对应 bin.xml 配置

2011.09.20: writen by hyw
"""

import engine
from libs import Path
from libs.Singleton import Singleton
from libs.SimpleXML import SimpleXML
from engine import Listener

# -------------------------------------------------------------------------
# system config
# -------------------------------------------------------------------------
class SysConfig(Singleton):
	def __init__(self):
		xml = SimpleXML(Path.executeDirectory())
		binSect = xml.openSection("bin.xml")
		if binSect is None:
			Listener().cbError("config file 'bin.xml' is not exist.")
			engine.exit(1)
		self.__binSect = binSect


	# ---------------------------------------------------------------------
	# properties
	# ---------------------------------------------------------------------
	@property
	def lngFile(self):
		"""
		语言配置文件
		"""
		lng = self.__binSect.readString("language")
		return "local/%s.xml" % lng

	@property
	def sysEncoding(self):
		"""
		运行系统的系统编码
		"""
		return self.__binSect.readString("sysEncoding").lower()

	@property
	def isDebug(self):
		"""
		是否启用调试
		"""
		return self.__binSect.readBool("debug")
