# -*- coding: utf-8 -*-
#

"""
实现 tars tag 配置 标记

2018.03.07: writen by hyw
"""

# --------------------------------------------------------------------
# 带属性的 Tars TAG
# --------------------------------------------------------------------
class TarsAttrTag(object):
	def __init__(self, keyExp, **attrs):
		self.keyExp = keyExp
		self.attrs = attrs

class _TarsAttrTag(object):
	def __init__(self, tagName, **attrs):
		self.tagName = tagName
		self.attrs = attrs


# --------------------------------------------------------------------
# 多维度值
# --------------------------------------------------------------------
class TarsListValue(object):
	def __init__(self, tagName, vlist):
		self.tagName = tagName
		self.values = vlist

class _TarsListValue(list):
	def __init__(self, tagName, values):
		super(_TarsListValue, self).__init__()
		index = -1
		if tagName == "" or tagName.endswith("+"):
			tagName = tagName[:-1]
			index = 0
		for value in values:
			if index >= 0:
				index += 1
			self.append((tagName + str(index), value))
