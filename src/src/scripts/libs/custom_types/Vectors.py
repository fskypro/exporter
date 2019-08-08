# -*- coding: utf-8 -*-
#

"""
实现向量

writen by hyw -- 2013.05.14
"""

import math
from abc import ABCMeta
from abc import abstractmethod

# --------------------------------------------------------------------
# Vector's base class
# --------------------------------------------------------------------
class Vector(object):
	def __init__(self):
		pass

	def __repr__(self):
		strElems = [str(e) for e in self]
		return "%s(%s)" % (self.__class__.__name__, ",".join(strElems))
	__str__ = __repr__

	@abstractmethod
	def __iter__(self):
		pass

	def __getitem__(self, index):
		selfIter = iter(self)
		tmp = 0
		value = None
		while tmp <= index:
			try:
				value = selfIter.next()
			except StopIteration:
				raise IndexError("%s index out of range." % self.__class__.__name__)
			tmp += 1
		return value


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def asTuple(self):
		return tuple(self)

	def asList(self):
		return list(self)

	def distTo(self, v):
		assert type(v) is type(self)
		powLens = 0
		for idx, e1 in enumerate(self):
			e2 = v[idx]
			powLens += math.pow(e1 - e2, 2)
		return math.sqrt(powLens)


# --------------------------------------------------------------------
# Vector2
# --------------------------------------------------------------------
class Vector2(Vector):
	def __init__(self, x=0, y=0):
		Vector.__init__(self)
		self.x, self.y = x, y

	def __iter__(self):
		yield self.x
		yield self.y


# --------------------------------------------------------------------
# Vector3
# --------------------------------------------------------------------
class Vector3(Vector):
	def __init__(self, x=0, y=0, z=0):
		Vector.__init__(self)
		self.x, self.y, self.z = x, y, z

	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z


# --------------------------------------------------------------------
# Vector4
# --------------------------------------------------------------------
class Vector4(Vector):
	def __init__(self, x=0, y=0, z=0, w=0):
		Vector.__init__(self)
		self.x, self.y, self.z, self.w = x, y, z, w

	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z
		yield self.w
