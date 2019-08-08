# -*- coding: utf-8 -*-
#

"""
可以被导出的自定义类型
"""

import re
from abc import ABCMeta
from abc import abstractmethod

# --------------------------------------------------------------------
# 用户自定义类型
# 除了在配置中写入 python 基本类型外，还可以写入自定义类型。但该自定义
# 类型必须继承于 CustomValue，并重新实现 __repr__ 方法，返回给导出时写
# 入配置用
# --------------------------------------------------------------------
class CustomType(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def __repr__(self):
		return object.__repr__(self)


# --------------------------------------------------------------------
# 字符串模板，导出为：
# string.Template("XXX")
# --------------------------------------------------------------------
class StringTemplate(CustomType):
	"""
	字符串模板对象
	"""
	def __init__(self, s):
		self.__str = re.sub(r'(?<=[^\\])"', r'\"', s)
	def __repr__(self):
		return 'string.Template("%s")' % self.__str
	def __cmp__(self, t):
		if isinstance(t, basestring):
			return self.__str != t
		return t.__str != self.__str
	def __hash__(self):
		return hash(self.__str)
