# -*- coding: utf-8 -*-
#

"""
实现可以指定小数点位数的浮点数

2011.09.20: writen by hyw
"""

class _XFloatMeta(type):
	def __eq__(cls, cls2):
		return isinstance(cls, _XFloatMeta) and isinstance(cls2, _XFloatMeta)

	def __cmp__(cls, cls2):
		if cls.__eq__(cls2):
			return 0
		return 1

	def __hash__(cls):
		return hash(_XFloatMeta)

class _XFloatWrapperMeta(_XFloatMeta):
	__clses = {}

	def __getitem__(cls, dds):
		c = cls.__clses.get(dds)
		if c is not None: return c
		class xfloat(float):
			__metaclass__ = _XFloatMeta
			__fmt = "%%0.%if" % dds
			def __repr__(self):
				return self.__fmt % float(float.__repr__(self))
			__str__ = __repr__
		cls.__clses[dds] = xfloat
		return xfloat

class xfloat(float):
	__metaclass__ = _XFloatWrapperMeta

	def __new__(cls, value):
		return float.__new__(float, value)
