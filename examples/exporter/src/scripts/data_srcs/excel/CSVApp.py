# -*- coding: utf-8 -*-
#

"""
带标题的 csv 表格
要求：传入的路径和文件名必须是 utf-8 编码

2011.09.20: writen by hyw
"""

import os
from libs import Path
from TextEncoder import script2sys
from TextEncoder import sys2script
from TextEncoder import dsrc2script
from data_srcs.DataSrcExceptions import DataSourceException
from data_srcs.DataSrcExceptions import CSVFixException
from ExcelSheet import ExcelSheet

# --------------------------------------------------------------------
# CSV 表格行
# --------------------------------------------------------------------
class _CSVRow(object):
	def __init__(self, index, dataLine, encoding):
		self.__index = index
		self.__dataLine = dataLine
		self.__encoding = encoding
		self.__cells = []

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def index(self):
		return self.__index


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __explain(self, index=-2):
		"""
		解释 csv
		1、列用逗号分隔
		2、列内容中，如果存在逗号，则列会被双引号包围
		3、列内容中，如果存在换行符“\n”，则列会被双引号包围
		4、列内容中，如果存在双引号，则单个双引号会变成两个双引号，并在外层再加一个双引号包围
		5、如果最后一列有内容，则内容后面不会再有“,”号了；如果最后一列没内容，则本行最后一个字符为“,”
		"""
		encoding = self.__encoding
		maxLen = index + 1
		cells = self.__cells
		dqm = 0														# 双引号个数
		cellText = ""
		dataLine = self.__dataLine
		count = len(dataLine)
		p = 0
		while p < count:
			char = dataLine[p]
			if char == "\"":
				if dqm <= 1:
					dqm += 1
				else:
					cellText += char								# 该双引号为有效内容
					dqm -= 1
			elif char == ",":
				if dqm % 2 == 0:									# 列分隔
					cells.append(dsrc2script(encoding, cellText))
					cellText = ""
					dqm = 0
					if 0 < maxLen <= len(cells):					# 只解释 index 前面的列
						p += 1
						break										# 跳出，不再解释 index 后面的列
				else:
					cellText += char
			else:
				cellText += char
			p += 1

		if len(cellText) or (0 < p == count):						# “0 < p == count”表示最后一列如果没有内容的话，是单纯一个“,”结束，所以要补一个空列
			cells.append(dsrc2script(encoding, cellText))
		self.__dataLine = dataLine[p:]


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getCell(self, index):
		if index < 0:
			raise IndexError("csv's row index out of range")
		if index >= len(self.__cells):
			self.__explain(index)
		return self.__cells[index]

	def getCellsCount(self):
		self.__explain()
		return len(self.__cells)

	def iterCells(self, index=None):
		if index is None:
			self.__explain()
		elif index < 0:
			raise IndexError("csv's row index out of range")
		else:
			self.__explain(index)
		for cell in self.__cells:
			yield cell

	def getCells(self, index=None):
		if index is None:
			self.__explain()
		elif index < 0:
			raise IndexError("csv's row index out of range")
		else:
			self.__explain(index)
		cells = []
		for cell in self.__cells:
			cells.append(cell)
		return cells


# --------------------------------------------------------------------
# CSV 表格
# --------------------------------------------------------------------
class CSVSheet(ExcelSheet):
	def __init__(self, fileName, dataLines, encoding):
		ExcelSheet.__init__(self, fileName, encoding)
		self.__rowDatas = []
		for index, dataLine in enumerate(dataLines):
			if len(dataLine) == 0: continue
			self.__rowDatas.append(_CSVRow(index, dataLine, encoding))
		if len(dataLines):
			self.__colCount = self.__rowDatas[0].getCellsCount()
		else:
			self.__colCount = 0


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def rowCount(self):
		return len(self.__rowDatas)

	@property
	def colCount(self):
		return self.__colCount

	# -------------------------------------------------
	def getText(self, row, col):
		if row >= self.rowCount:
			raise IndexError("row index(%i) out of range." % row)
		if col >= self.colCount:
			raise IndexError("column index(%i) out of range." % col)
		rowData = self.__rowDatas[row]
		if col >= self.__colCount:
			return ""
		return rowData.getCell(col)

	# -------------------------------------------------
	def iterColText(self, col):
		if col >= self.colCount:
			raise IndexError("column index(%i) out of range." % col)
		if col >= self.__colCount:
			for row in xrange(self.rowCount):
				yield ""
		else:
			for row in xrange(self.rowCount):
				yield self.__rowDatas[row].getCell(col)

	def iterRowText(self, row):
		if row >= self.rowCount:
			raise IndexError("row index(%i) out of range." % row)
		for cellText in self.__rowDatas[row].iterCells():
			yield cellText

	def iterRangeText(self, row1, col1, row2, col2):
		datas = []
		row1 = max(0, min(row1, self.rowCount-1))
		col1 = max(0, min(col1, self.__colCount-1))
		if row1 < row2: row1, row2 = row2, row1
		if col1 < col2: col1, col2 = col2, col1
		colCount = self.__colCount
		for row in xrange(row1, row2+1):
			rowData = self.__rowDatas[row]
			for col in xrange(col1, col2+1):
				if col >= colCount:
					yield ""
				else:
					yield rowData.getCell(col)


# --------------------------------------------------------------------
# CSV 解释器
# --------------------------------------------------------------------
class CSVApp(object):
	__inst = None

	def __init__(self):
		assert (CSVApp.__inst is None)
		CSVApp.__inst = self
		self.__sheets = {}

	@staticmethod
	def inst():
		if CSVApp.__inst is None:
			CSVApp.__inst = CSVApp()
		return CSVApp.__inst


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSheet(self, fileName, encoding):
		"""
		获取一个 CSV 表格
		fileName 的编码必须与本程序脚本使用的编码一致
		"""
		fileName = Path.normalizePath(fileName)
		sysFileName = script2sys(fileName)
		if fileName in self.__sheets:
			return self.__sheets[fileName]
		if not os.path.exists(sysFileName):
			raise CSVFixException("errUnexist", file=fileName)
		try:
			file = open(sysFileName, "rb")
		except Exception, err:
			raise DataSourceException(sys2script(err.__str__()))
		dataLines = file.read().split("\r\n")
		csvSheet = CSVSheet(fileName, dataLines, encoding)
		self.__sheets[fileName] = csvSheet
		return csvSheet
