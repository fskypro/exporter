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


# --------------------------------------------------------------------
# 多维度值
# --------------------------------------------------------------------
class XMLListValue(object):
	def __init__(self, tag, vlist):
		self.tag = tag
		self.vlist = vlist
