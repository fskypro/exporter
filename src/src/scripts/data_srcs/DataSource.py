# -*- coding: utf-8 -*-
#

"""
解释器用的二维表格

2011.09.20: writen by hyw
"""

import os
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from libs import Path
from TextEncoder import script2sys
from engine import Listener
from config.Local import Local
from config.CustomConfig import CustomConfig
from Exceptions import BaseException
from DataSrcExceptions import DataSourceFixException


# --------------------------------------------------------------------
# global functions
# --------------------------------------------------------------------
def getSrcFullName(srcFile):
	"""
	获取数据源文件全路径
	"""
	for root in CustomConfig().srcRoots:
		fullName = os.path.join(root, srcFile)
		fullName = Path.normalizePath(fullName)
		if os.path.exists(script2sys(fullName)):
			return fullName
	return srcFile

def getConfigEncoding(extention):
	"""
	获取配置中设置的编码
	"""
	ext = CustomConfig().query("dataSource/encodings/%s" % extention, str)
	if ext == "":
		return CustomConfig().query("dataSource/encodings" % extention, str)
	return ext


# --------------------------------------------------------------------
# 数据源信息抽象基类
# 每类型数据源都必须有自己的数据源信息类，并且必须继承于该类
# attrs 可以包含以下键:
# 	rowCount: 导出的行数
# --------------------------------------------------------------------
def _raiseUnImplementExcept(clsName, methodName):
	raise BaseException("unimplement exception", "method '%s' is not implemented.")

class iDataSource(object):
	__metaclass__ = ABCMeta

	def __init__(self, headRow, startRow, loadTime=0.0, **attrs):
		self.__headRow = headRow					# 表头所在行索引
		self.__startRow = startRow					# 数据内容起始行
		self.__loadTime = loadTime					# 数据源加载时间
		self.__attrs = attrs						# 额外属性
		self.rowCount_ = attrs.get("rowCount", -1)	# 指定导出行数

		self.name2col_ = {}
		self.__initHeads(headRow)
		_cacheTables.add(self)

	def dispose(self):
		if self in _cacheTables:
			_cacheTables.remove(self)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def clsName(self):
		return self.__class__.__name__

	@property
	def heads(self):
		return dict(self.name2col_)

	@property
	def headRow(self):
		return self.__headRow

	@property
	def startRow(self):
		return self.__startRow

	# -------------------------------------------------
	@property
	def loadTime(self):
		return self.__loadTime

	# -------------------------------------------------
	@abstractproperty
	def rowCount(self):
		"""
		获取行数
		"""
		return self.rowCount_

	@abstractproperty
	def colCount(self):
		"""
		获取列数
		"""
		pass


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initHeads(self, headRow):
		for col, cname in enumerate(self.iterRowText(headRow)):
			cname = cname.strip()
			if cname == "": continue
			c = self.name2col_.get(cname)
			if c is not None:																# 列明重复
				Listener().cbWarning(Local().formatLocalText("dataSource", "warnDBHeadName", \
					col1=self.col2mark(c), col2=self.col2mark(col), name=cname))
			self.name2col_[cname] = col

	def query(self, attrName, attrType):
		"""
		获取额外属性
		"""
		if attrName not in self.__attrs:
			self.__attrs[attrName] = CustomConfig().query("dataSource/%s" % attrName, attrType)
		return self.__attrs[attrName]


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def col2mark(col):
		"""
		获取指定索引列的列代称
		"""
		return str(col)

	# -------------------------------------------------
	def name2col(self, name):
		"""
		将列名转化为列索引
		"""
		try:
			return self.name2col_[name]
		except KeyError, err:
			raise DataSourceFixException("errNoTableHead", src=self.getSrcText(), col=name)

	# -------------------------------------------------
	@abstractmethod
	def getText(self, row, col):
		"""
		获取指定单元格内容
		"""
		pass

	@abstractmethod
	def setText(self, row, col, text):
		"""
		设置指定单元格内容
		"""
		pass

	# -------------------------------------------------
	@abstractmethod
	def getRangeText(self, row1, col1, row2, col2):
		"""
		获取指定区域的内容，返回一个二维列表
		"""
		pass

	@abstractmethod
	def setRangeText(self, row, col, datas):
		"""
		设置指定区域内容，datas 为一个二维列表
		"""
		pass

	# -------------------------------------------------
	@abstractmethod
	def iterColText(self, col):
		"""
		迭代指定列的所有行内容
		"""
		pass

	@abstractmethod
	def iterRowText(self, row):
		"""
		迭代指定行的所有列内容
		"""
		pass

	@abstractmethod
	def iterRangeText(self, row1, col1, row2, col2):
		"""
		迭代指定范围格子内容
		"""
		pass

	# -------------------------------------------------
	@abstractmethod
	def getSrcText(self):
		"""
		获取一段文本，用以描述数据的来源
		"""
		return ""


# --------------------------------------------------------------------
# global functions
# --------------------------------------------------------------------
_cacheTables = set()
def onAppExit(exitCode):
	"""
	程序退出时调用
	"""
	for table in set(_cacheTables):
		table.dispose()
Listener().cbAppExit.bind(onAppExit)
