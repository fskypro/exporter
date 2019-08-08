# -*- coding: utf-8 -*-
#

"""
加载数据源跟踪器

2011.09.20: writen by hyw
"""

from engine import Listener

class LoadDataTracer(object):
	def __init__(self, srcText):
		self.__srcText = srcText
		self.__dsrc = None
		self.__loadTime = 0


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def loadTime(self):
		return self.__loadTime

	@property
	def dsrc(self):
		return self.__dsrc


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onBeginLoad(self):
		Listener().cbBeginLoadDataSource(self)
		Listener().cbLoadingDataSource(self, 0.0)

	def onLoadProgress(self, progress):
		Listener().cbLoadingDataSource(self, progress)

	def onEndLoad(self, dsrc, loadTime):
		self.__dsrc = dsrc
		self.__loadTime = loadTime
		Listener().cbEndLoadDataSource(self)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSrcText(self):
		return self.__srcText
