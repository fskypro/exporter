# -*- coding: utf-8 -*-
#

"""
实现类似 C++ 中的友员

使用实例：
from FriendMethod import FriendMethodMeta
from FriendMethod import friendmethod
class A(object):
	__metaclass__ = FriendMethodMeta

	@friendmethod("B")			# 将函数 __func 设置为名称为“B”的类的友员
	def __func1(self):
		pass

	@friendmethod("B", "C")
	def __func2(self):
		pass

class B(object):
	def __init__(self):
		A().__func1()			# 可以访问 A 的私有成员

class C(object):
	def __init__(self):
		A().__func2()			# 可以访问 A 的私有成员

注意：非异常安全（因为是“元类”实现，所以无关要紧）

records:
	writen by yongwei-huang -- 2013.03.19
"""

import re

# --------------------------------------------------------------------
# inner functions
# --------------------------------------------------------------------
def _isPrivateAttributeName(name):
	if re.search("^__\w+$", name):
		return not name.endswith("__")
	return False

def _exposePrivateAttributeName(clsName, attrName):
	if not _isPrivateAttributeName(attrName):
		return attrName
	return "_" + re.findall("^_*(\w+)", clsName)[0] + attrName


# --------------------------------------------------------------------
# implement friend method
# --------------------------------------------------------------------
class FriendMethodMeta(type):
	def __init__(cls, clsName, bases, metaInfo):
		friendMethods = friendmethod.__friend_method_cache__
		friendmethod.__friend_method_cache__ = {}
		for mname, func in friendMethods.iteritems():
			setattr(cls, mname, func)

class friendmethod(object):
	__friend_method_cache__ = {}

	def __init__(self, *clsNames):
		self.__clsNames = clsNames

	def __call__(self, func):
		if _isPrivateAttributeName(func.func_name):
			for clsName in self.__clsNames:
				exposedName = _exposePrivateAttributeName(clsName, func.func_name)
				self.__friend_method_cache__[exposedName] = func
			return func
