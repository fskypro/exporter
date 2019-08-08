# -*- coding: utf-8 -*-
#

"""
配置异常

2011.09.20: writen by hyw
"""

from Local import Local
from Exceptions import BaseException

class ConfigFixException(BaseException):
	def __init__(self, tagName, **args):
		title = Local().formatLocalText("config", "errTitle")
		msg = Local().formatLocalText("config", tagName, **args)
		BaseException.__init__(self, title, msg)

class ConfigTagPathException(ConfigFixException):
	"""
	配置 xml 路径不存在
	"""
	def __init__(self, path):
		ConfigFixException.__init__(self, "errTagUnexist", path=path)

class ConfigTagValueException(ConfigFixException):
	"""
	配置值不正确
	"""
	def __init__(self, tag):
		ConfigFixException.__init__(self, "errValueError", tag=tag)
