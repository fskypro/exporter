# -*- coding: utf-8 -*-
#

"""
要求：
	① python 2.6 及 pywin32-214.win32-py2.6.exe 及 ms office
	② 传入的路径和文件名必须是 utf-8 编码

2011.09.20: writen by hyw
"""

import os
import math
import xlrd
from libs import Path
from libs.Singleton import Singleton
from engine import Listener
from data_srcs.DataSrcExceptions import ExcelComException
from data_srcs.DataSrcExceptions import ExcelInEditException
from data_srcs.DataSrcExceptions import ExcelFixException
from TextEncoder import dsrc2script
from TextEncoder import script2dsrc
from TextEncoder import script2sys
from TextEncoder import sys2script
from ExcelSheet import ExcelSheet

# --------------------------------------------------------------------
# Excel 工作簿分页
# 注意：
#     获取的表格内容全部与程序脚本编码相同，要求设置的内容也要与程序脚本相同
# --------------------------------------------------------------------
class XLSXSheet(ExcelSheet):
	def __init__(self, fileName, sheet, encoding):
		ExcelSheet.__init__(self, fileName, encoding)
		self.sheet_ = sheet


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def baseSheet(self):
		return self.sheet_

	# -------------------------------------------------
	@property
	def name(self):
		return dsrc2script(self.encoding, self.sheet_.name)

	@property
	def rowCount(self):
		return self.sheet_.nrows

	@property
	def colCount(self):
		return self.sheet_.ncols


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getText(self, row, col):
		"""
		xlrd 自动类型识别，并且将整型变为 float 型返回
		"""
		value = self.sheet_.cell(row, col).value
		if isinstance(value, basestring):
			return dsrc2script(self.encoding, value)
		elif type(value) is float and value % 1 == 0.0:
			return str(int(value))
		return str(value)

	def setText(self, row, col, text):
		self.sheet_.write(row, col, text)

	def getRangeText(self, row1, col1, row2, col2):
		rowDatas = []
		for row in xrange(row1, row2+1):
			rowData = []
			for col in xrange(col1, col2+1):
				rowData.append(self.getText(row, col))
			rowDatas.append(rowData)
		return rowDatas

	def setRangeText(self, row, col, datas):
		"""
		设置指定区域内容，datas 为一个二维列表
		"""
		for rowIdx in xrange(row, row + len(datas)):
			data = datas[rowIdx-row]
			for colIdx in xrange(col, len(data)):
				self.sheet_.write(rowIdx, colIdx, data[colIdx-col])

	def iterRangeText(self, row1, col1, row2, col2):
		"""
		获取指定区域内容
		"""
		for row in xrange(row1, row2+1):
			for col in xrange(col1, col2+1):
				yield self.getText(row, col)

	def iterColText(self, col):
		"""
		获取指定列的所有行迭代器
		"""
		for row in xrange(self.rowCount):
			yield self.getText(row, col)

	def iterRowText(self, row):
		"""
		获取指定行的所有列迭代器
		"""
		for col in xrange(self.colCount):
			yield self.getText(row, col)

# --------------------------------------------------------------------
# Excel 阅读器
# --------------------------------------------------------------------
class XLSXApp(Singleton):
	def __init__(self):
		self.__wbooks = {}


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getWorkbook(self, fileName, encoding):
		"""
		获取 Excel 工作簿
		Excel 文件不存在，或者 Excel 在操作中，则引起 ExcelComException
		fileName 的编码必须与本程序脚本使用的编码一致
		"""
		fileName = Path.normalizePath(fileName)
		if fileName in self.__wbooks:
			return self.__wbooks[fileName]
		sysFileName = script2sys(fileName)
		sysFileName = Path.normalizePath(sysFileName)
		if not os.path.exists(sysFileName):
			raise ExcelFixException("errUnexist", file=fileName)
		try:
			wbook = xlrd.open_workbook(sysFileName)
			self.__wbooks[fileName] = wbook
			return wbook
		except xlrd.XLRDError, err:
			raise ExcelFixException("errUnexist", file=fileName)

	def getSheet(self, fileName, sheetName, encoding):
		"""
		获取 Excel 分页
		fileName、sheetName 的编码必须与本程序脚本使用的编码一致
		"""
		book = self.getWorkbook(fileName, encoding)
		dsrcSheetName = script2dsrc(encoding, sheetName)
		baseSheet = None
		try:
			baseSheet = book.sheet_by_name(dsrcSheetName)
		except xlrd.XLRDError, err:
			raise ExcelFixException("errSheetUnexist", file=fileName, sheet=sheetName)
		return XLSXSheet(fileName, baseSheet, encoding)

	def close(self, save=False):
		"""
		关闭 excel 程序
		"""
		if save:
			for fileName, wbook in self.__wbooks.iteritems():
				try:
					wbook.save(script2sys(fileName))
				except Exception, err:
					raise ExcelFixException("errSave", file=fileName, msg=err.message)
		Listener().cbLocalMsg("excelApp", "tipsReleaseExcel")


# --------------------------------------------------------------------
# global functions
# --------------------------------------------------------------------
def onAppExit(exitCode):
	"""
	程序退出时调用
	"""
	XLSXApp.inst().close(False)
	XLSXApp.releaseInst()
Listener().cbAppExit.bind(onAppExit)
