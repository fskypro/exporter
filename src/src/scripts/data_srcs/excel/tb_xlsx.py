# -*- coding: utf-8 -*-
#

"""
带标题的 excel 表格
要求：传入的路径和文件名必须是 utf-8 编码

2011.09.20: writen by hyw
"""

import time
from TextEncoder import script2sys
from config.CustomConfig import CustomConfig
from data_srcs.DataSource import iDataSource
from data_srcs.DataSource import getSrcFullName
from data_srcs.DataSource import getConfigEncoding
from data_srcs.LoadDataTracer import LoadDataTracer
from XLSXApp import XLSXApp


# --------------------------------------------------------------------
# implement table(excel sheet contains headers)
# --------------------------------------------------------------------
class XLSXSource(iDataSource):
	def __init__(self, sheet, headRow, startRow, loadTime, **attrs):
		self.__sheet = sheet
		iDataSource.__init__(self, headRow, startRow, loadTime, **attrs)

	def dispose(self):
		for key, table in _g_dsrcs.items():
			if table == self:
				_g_dsrcs.pop(key)
				break
		iDataSource.dispose(self)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
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
		"""
		设置指定单元格内容
		"""
		self.__sheet.setText(row, col, text)

	# -------------------------------------------------
	def getRangeText(self, row1, col1, row2, col2):
		if type(col1) is str: col1 = self.name2col_[col1]
		if type(col2) is str: col2 = self.name2col_[col2]
		return self.__sheet.getRangeText(row1, col1, row2, col2)

	def setRangeText(self, row, col, datas):
		"""
		设置指定区域内容，datas 为一个二维列表
		"""
		self.sheet_.setRangeText(row, col, datas)

	# -------------------------------------------------
	def iterColText(self, col):
		if type(col) is not int:
			col = self.name2col_[col]
		return self.__sheet.iterColText(col)

	def iterRowText(self, row):
		return self.__sheet.iterRowText(row)

	def iterRangeText(self, row1, col1, row2, col2):
		if type(col1) is not int: col1 = self.name2col_[col1]
		if type(col2) is not int: col2 = self.name2col_[col2]
		return self.__sheet.iterRangeText(row1, col1, row2, col2)

	# -------------------------------------------------
	def getSrcText(self):
		"""
		获取一段文本，用以描述数据的来源
		"""
		return "%s::[%s]" % (self.__sheet.fileName, self.__sheet.name)


# -------------------------------------------------------------------------
# xls, xlsx, xlsm 等 excel 原始数据源
# -------------------------------------------------------------------------
_g_dsrcs = {}
def getDataSource(fileName, sheetName, headRow, startRow, **attrs):
	"""
	获取一个 Excel 表格（"xlsx", "xls", "xlsm"），返回：XLSXSource
	Excel 文件不存在，或者 Excel 在操作中，则引起 ExcelComException
	分页不存在，则返回 None
	fileName、sheetName 的编码必须与本程序脚本使用的编码一致

	attrs 目前支持：
		encoding: 表示数据源使用的编码，如果不传入，则使用 config.xml 中配置的默认编码
	"""
	fileName = getSrcFullName(fileName)
	key = (fileName, sheetName)
	dsrc = _g_dsrcs.get(key)
	if dsrc is not None: return dsrc

	# 加载数据源
	start = time.time()
	loadTracer = LoadDataTracer("%s::[%s]" % (fileName, sheetName))
	loadTracer.onBeginLoad()													# 回调开始加载
	encoding = attrs.get("encoding", getConfigEncoding("xlsx"))
	sheet = XLSXApp.inst().getSheet(fileName, sheetName, encoding)
	loadTracer.onLoadProgress(1.0)												# 回调加载进度
	loadTime = time.time() - start
	dsrc = XLSXSource(sheet, headRow, startRow, loadTime, **attrs)
	loadTracer.onEndLoad(dsrc, loadTime)										# 回调加载结束

	# 缓存数据
	_g_dsrcs[key] = dsrc
	return dsrc
