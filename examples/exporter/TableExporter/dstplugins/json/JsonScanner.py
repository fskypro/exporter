# -*- coding: utf-8 -*-
#

"""
扫描数据源

2014.04.15: writen by hyw
"""

from exporter.pydict.PyDictScanner import PyDictScanner


# --------------------------------------------------------------------
# 导出解释器，对应每一个 data_srcs/DataSource::iDataSource 的子类
# --------------------------------------------------------------------
class JsonScanner(PyDictScanner):
	def __init__(self, outItemInfo):
		PyDictScanner.__init__(self, outItemInfo)
