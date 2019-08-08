# -*- coding: utf-8 -*-
#

"""
实现 XML 标记

2013.03.21: writen by hyw
"""

# --------------------------------------------------------------------
# 带属性的 XML TAG
# --------------------------------------------------------------------
class XMLAttrTag(object):
	def __init__(self, keyExp, **attrs):
		self.keyExp = keyExp
		self.attrs = attrs

class _XMLAttrTag(object):
	def __init__(self, tagName, **attrs):
		self.tagName = tagName
		self.attrs = attrs


# --------------------------------------------------------------------
# 多维度值
# --------------------------------------------------------------------
class XMLListValue(object):
	def __init__(self, tagName, vlist):
		self.tagName = tagName
		self.values = vlist

class _XMLListValue(list):
	def __init__(self, tagName, values):
		super(_XMLListValue, self).__init__()
		index = -1
		if tagName == "" or tagName.endswith("+"):
			tagName = tagName[:-1]
			index = 0
		for value in values:
			if index >= 0:
				index += 1
			self.append((tagName + str(index), value))
