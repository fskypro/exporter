# -*- coding: utf-8 -*-
#

"""
excel 表格

2011.09.20: writen by hyw
"""

from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

class ExcelSheet(object):
	__metaclass__ = ABCMeta

	def __init__(self, fileName, encoding):
		self.__fileName = fileName
		self.__encoding = encoding


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def fileName(self):
		return self.__fileName

	@property
	def encoding(self):
		return self.__encoding

	# -------------------------------------------------
	@abstractproperty
	def rowCount(self):
		return 0

	@abstractproperty
	def colCount(self):
		return 0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def col2CharsCol(col):
		"""
		将以 0 开始的列号转换为 Excel 表中的大写字母表示的列号
		"""
		charCol = ""
		resudue = max(0, col)
		n = 0
		while True:											# 转换为 26 进制
			downBase = 26 ** n
			upBase = 26 * downBase
			value = (resudue % upBase) / downBase
			resudue -= value * downBase
			charCol = chr(value + ord('A')) + charCol
			if resudue <= 0: break
			n += 1
		if n > 0:
			charCol = chr(ord(charCol[0])-1) + charCol[1:]	# 做这个操作的原因是 Excel 表格列号可以以 A 为开头（即 0 开头）
		return charCol

	# -------------------------------------------------
	@abstractmethod
	def getText(self, row, col):
		pass

	@abstractmethod
	def iterColText(self, col):
		pass

	@abstractmethod
	def iterRowText(self, row):
		pass
