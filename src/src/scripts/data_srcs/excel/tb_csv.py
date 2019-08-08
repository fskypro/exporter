# -*- coding: utf-8 -*-
#

"""
带标题的 csv 表格
要求：传入的路径和文件名必须是 utf-8 编码

2011.09.20: writen by hyw
"""

import time
from libs import Path
from TextEncoder import script2sys
from config.CustomConfig import CustomConfig
from data_srcs.DataSource import iDataSource
from data_srcs.DataSource import getSrcFullName
from data_srcs.DataSource import getConfigEncoding
from data_srcs.LoadDataTracer import LoadDataTracer
from CSVApp import CSVApp


# --------------------------------------------------------------------
# implement csv data table
# --------------------------------------------------------------------
class CSVSource(iDataSource):
	def __init__(self, sheet, headRow, startRow, loadTime, **attrs):
		self.__sheet = sheet
		iDataSource.__init__(self, headRow, startRow, loadTime, **attrs)

	def dispose(self):
		iDataSource.dispose(self)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def fileName(self):
		return Path.normalizePath(self.__sheet.fileName)

	@property
	def rowCount(self):
		if self.rowCount_ < 0:
			return self.__sheet.rowCount
		return self.rowCount_

	@property
	def colCount(self):
		return self.__sheet.colCount


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def col2mark(self, col):
		return self.__sheet.col2CharsCol(col)

	# -------------------------------------------------
	def getText(self, row, col):
		if type(col) is not int:
			col = self.name2col_[col]
		return self.__sheet.getText(row, col)

	def setText(self, row, col, text):
		if type(col) is not int:
			col = self.name2col_[col]
		self.__sheet.setText(row, col, text)

	# -------------------------------------------------
	def getRangeText(self, row1, col1, row2, col2):
		if type(col1) is str: col1 = self.name2col_[col1]
		if type(col2) is str: col2 = self.name2col_[col2]
		return self.__sheet.getRangeText(row1, col1, row2, col2)

	def setRangeText(self, row, col, datas):
		if type(col) is not int:
			col = self.name2col_[col]
		self.__sheet.setRangeText(row, col, datas)

	# -------------------------------------------------
	def iterColText(self, col):
		if type(col) is not int:
			col = self.name2col_[col]
		return self.__sheet.iterColText(col)

	def iterRowText(self, row):
		return self.__sheet.iterRowText(row)

	def iterRangeText(self, row1, col1, row2, col2):
		if type(col1) is str: col1 = self.name2col_[col1]
		if type(col2) is str: col2 = self.name2col_[col2]
		return self.__sheet.iterRangeText(row1, col1, row2, col2)

	# -------------------------------------------------
	def getSrcText(self):
		"""
		获取一段文本，用以描述数据的来源
		"""
		return self.fileName


# -------------------------------------------------------------------------
# csv 数据源
# -------------------------------------------------------------------------
def getDataSource(fileName, headRow, startRow, **attrs):
	"""
	获取一个 CSV 数据源，返回：CSVSource
	csv 文件不存在，则引起 CSVFixException
	无法打开或无法读取或解释 csv 文件，则引起 DataSourceException
	fileName 的编码必须与本程序脚本使用的编码一致

	attrs 目前支持：
		encoding: 表示数据源使用的编码，如果不传入，则使用 config.xml 中配置的默认编码
	"""
	fileName = getSrcFullName(fileName)

	# 加载数据源
	start = time.time()
	loadTracer = LoadDataTracer(fileName)
	loadTracer.onBeginLoad()												# 回调开始加载
	encoding = attrs.get("encoding", getConfigEncoding("csv"))
	sheet = CSVApp.inst().getSheet(fileName, encoding)
	loadTracer.onLoadProgress(1.0)										# 回调加载进度
	loadTime = time.time() - start
	dsrc = CSVSource(sheet, headRow, startRow, loadTime, **attrs)
	loadTracer.onEndLoad(dsrc, loadTime)								# 回调加载结束

	return dsrc
