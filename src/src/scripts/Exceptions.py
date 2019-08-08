# -*- coding: utf-8 -*-
#

"""
自定义异常

2011.09.20: writen by hyw
"""

from libs.encode import sys2script
from libs.encode import script2sys

# --------------------------------------------------------------------
# 异常基类
# --------------------------------------------------------------------
class BaseException(Exception):
	"""
	异常基类
	"""
	def __init__(self, title, msg):
		"""
		title 为异常标题（编码与脚本编码一致）
		msg 为异常信息（编码与脚本编码一致）
		"""
		self.__message = script2sys("%s\n  %s" % (title, msg))
		Exception.__init__(self, self.__message)

	@property
	def message(self):
		"""
		返回的消息编码为系统编码，并非脚本编码
		"""
		return self.__message

	@property
	def scriptMsg(self):
		"""
		返回脚本编码的异常消息
		"""
		return sys2script(self.__message)

	@property
	def sysMsg(self):
		"""
		返回与系统编码一致的异常消息
		"""
		return self.__message
