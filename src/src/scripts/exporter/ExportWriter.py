# -*- coding: utf-8 -*-
#

"""
写出工具基类

2014.03.19: writen by hyw
"""

from abc import ABCMeta
from abc import abstractmethod

class ExportWriter(object):
	__metaclass__ = ABCMeta

	def __init__(self, exportTracer):
		self.__exportTracer = exportTracer


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def exportTracer(self):
		return self.__exportTracer

	@property
	def outInfo(self):
		return self.__exportTracer.outInfo


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@abstractmethod
	def close(self):
		pass

	@abstractmethod
	def writeText(self, text):
		"""
		允许写出一段文本
		"""
		pass

	@abstractmethod
	def writeOutItem(self, outItemTracer):
		"""
		写出一个表格行
		"""
		pass
