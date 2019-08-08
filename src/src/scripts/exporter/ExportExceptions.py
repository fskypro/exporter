# -*- coding: utf-8 -*-
#

"""
导出异常

2011.09.20: writen by hyw
"""

from config.Local import Local
from Exceptions import BaseException


class ExportException(BaseException):
	"""
	导出异常
	"""
	def __init__(self, msg):
		title = Local().formatLocalText("export", "errTitle")
		BaseException.__init__(self, title, msg)

class ExportFixException(ExportException):
	"""
	能明确知道错误的导出异常
	"""
	def __init__(self, tagName, **args):
		msg = Local().formatLocalText("export", tagName, **args)
		ExportException.__init__(self, msg)
