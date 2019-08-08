# -*- coding: utf-8 -*-
#

import re
import operator

# --------------------------------------------------------------------
# 导出配置的类型
# --------------------------------------------------------------------
class metahint(type):
	__reptn = re.compile("^(:?0|(:?-0))[xX][\dabcdef]+?$")

	def __init__(cls, name, bases, dict):
		super(metahint, cls).__init__(name, bases, dict)
		cls.__new__ = staticmethod(metahint.__replace_new)
		cls.__cache = {}

	@staticmethod
	def __replace_new(cls, value=0, sites=0):
		if type(value) is cls:
			value = value.asInt
		elif isinstance(value, basestring):
			if hlint.__reptn.search(value):
				value = int(value, 16)
			else:
				try:
					value = int(value)
				except ValueError:
					raise ValueError("invalid literal for hlint() with base 10: %r" % value)
		else:
			try:
				value = int(value)
			except TypeError:
				raise TypeError("hlint() argument must be a string or a hlint or a number, not %r" % type(value))
		hLInt = cls.__cache.get(value)
		if hLInt is not None: return hLInt
		hLInt = object.__new__(cls)
		hLInt._hlint__asInt = value
		cls.__cache[value] = hLInt
		return hLInt

	def __repr__(cls):
		return "<type 'hlint'>"


class hlint(object):
	__metaclass__ = metahint
	__slots__ = ("__asInt", "__sites")

	def __init__(self, value=0, sites=0):
		self.__sites = sites						# 位数，如：如果 sites == 4 则 0x22 表示为 0x0022

	@property
	def asInt(self):
		return self.__asInt

	@property
	def asLong(self):
		return long(self.__asInt)

	@property
	def asFloat(self):
		return float(self.__asInt)

	@property
	def sites(self):
		return self.__sites


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __repr__(self):
		asInt = self.__asInt
		if asInt >= 0:
			if type(asInt) is long:
				return ("0x%%0%dxL" % self.__sites) % asInt
			return ("0x%%0%dx" % self.__sites) % asInt
		else:
			asInt = -asInt
			if type(asInt) is long:
				return ("-0x%%0%dxL" % self.__sites) % asInt
			return ("-0x%%0%dx" % self.__sites) % asInt
	__str__ = __repr__

	def __eq__(self, value):
		if type(value) is hlint:
			return value.__asInt == self.__asInt
		return value == self.__asInt

	def __cmp__(self, value):
		if type(value) is hlint:
			return value.__asInt - self.__asInt
		try:
			return self.__asInt - value
		except:
			return 0

	def __hash__(self):
		return hash(self.__asInt)

	def __abs__(self):
		return hlint(abs(self.__asInt))

	def __add__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt.__add__(self.__asInt))
		return hlint(self.__asInt + value)

	def __radd__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt + self.__asInt)
		return hlint(value + self.__asInt)

	def __and__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt & self.__asInt)
		return hlint(self.__asInt & value)

	def __rand__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt & self.__asInt)
		return hlint(value & self.__asInt)

	def __or__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt | self.__asInt)
		return hlint(self.__asInt | value)

	def __ror__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt | value.__asInt)
		return hlint(value | self.__asInt)

	def __xor__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt ^ self.__asInt)
		return hlint(self.__asInt ^ value)

	def __rxor__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt ^ value.__asInt)
		return hlint(value ^ self.__asInt)

	def __coerce__(self, value):
		if type(value) is hlint:
			return (self, value)
		return (self, hlint(value))

	def __delattr__(self, name):
		if hasattr(self, name):
			raise AttributeError("attribute %r of 'hlint' objects is not writable" % name)
		else:
			raise AttributeError("'hlint' object has no attribute %r" % name)

	def __div__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt / value.__asInt)
		return hlint(self.__asInt / value)

	def __rdiv__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt / self.__asInt)
		return hlint(value / self.__asInt)

	def __divmod__(self, value):
		if type(value) is hlint:
			div, mod = divmod(self.__asInt, value.__asInt)
		else:
			div, mod = divmod(self.__asInt, value)
		return hlint(div), hlint(mod)

	def __rdivmod__(self, value):
		if type(value) is hlint:
			div, mod = divmod(value.__asInt, self.__asInt)
		else:
			div, mod = divmod(value, self.__asInt)
		return hlint(div), hlint(mod)

	def __float__(self):
		return self.__asInt.__float__()

	def __floordiv__(self, value):
		if type(value) is hlint:
			return hlint(operator.floordiv(self.__asInt, value.__asInt))
		return hlint(operator.floordiv(self.__asInt, value))

	def __rfloordiv__(self, value):
		if type(value) is hlint:
			return hlint(operator.floordiv(value.__asInt, self.__asInt))
		return hlint(operator.floordiv(value, self.__asInt))

	def __truediv__(self, value):
		if type(value) is hlint:
			return hlint(operator.truediv(self.__asInt, value.__asInt))
		return hlint(operator.truediv(self.__asInt, value))

	def __rtruediv__(self, value):
		if type(value) is hlint:
			return hlint(operator.truediv(value.__asInt, self.__asInt))
		return hlint(operator.truediv(value, self.__asInt))

	def __format__(self, format_spec):
		return hlint(self.__asInt.__format__(format_spec))

	def __hex__(self):
		return hex(self.__asInt)

	def __index__(self):
		return self.__asInt.__index__()

	def __int__(self):
		return self.__asInt

	def __invert__(self):
		return hlint(~self.__asInt)

	def __long__(self):
		return self.__asInt.__long__()

	def __lshift__(self, count):
		if type(count) is hlint:
			return hlint(self.__asInt << count.__asInt)
		return hlint(self.__asInt << count)

	def __rlshift__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt << self.__asInt)
		return hlint(value << self.__asInt)

	def __rshift__(self, count):
		if type(count) is hlint:
			return hlint(self.__asInt >> count.__asInt)
		return hlint(self.__asInt >> count)

	def __rrshift__(self, value):
		if type(value) is hlint:
			return hlint(value.asInt >> self.__asInt)
		return hlint(value >> self.__asInt)

	def __mod__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt % value.__asInt)
		return hlint(self.__asInt % value)

	def __rmod__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt % self.__asInt)
		return hlint(value % self.__asInt)

	def __mul__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt * value.__asInt)
		return hlint(self.__asInt * value)

	def __rmul__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt * value.__asInt)
		return hlint(self.__asInt * value)

	def __neg__(self):
		return hlint(self.__asInt.__neg__())

	def __nonzero__(self):
		return self.__asInt.__nonzero__()

	def __oct__(self):
		return self.__asInt.__oct__()

	def __pos__(self):
		return self.__asInt.__pos__()

	def __pow__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt ** value.__asInt)
		return hlint(self.__asInt ** value)

	def __rpow__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt ** self.asInt)
		return hlint(value ** self.__asInt)

	def __sub__(self, value):
		if type(value) is hlint:
			return hlint(self.__asInt - value.__asInt)
		return hlint(self.__asInt - value)

	def __rsub__(self, value):
		if type(value) is hlint:
			return hlint(value.__asInt - self.__asInt)
		return hlint(value - self.__asInt)
