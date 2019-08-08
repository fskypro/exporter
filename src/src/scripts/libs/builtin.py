# -*- coding: utf-8 -*-

"""
定义一些全局小函数

records:
	writen by yongwei-huang -- 2013.12.11
"""

import __builtin__
import collections

def iterable(obj):
	"""
	判断指定对象是否可以迭代
	"""
	return isinstance(obj, collections.Iterable)
__builtin__.iterable = iterable
