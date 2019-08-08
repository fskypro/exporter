# -*- coding: utf-8 -*-
#

"""
实现类似 C++ 中的枚举
匿名枚举定义方法：            命名枚举定义方法：             |   指定枚举按乘 2 递增的方法：                            不指定模块，指定枚举按乘 2 递增的方法：
aa.py：                       aa.py：                        |   aa.py：                                                aa.py：
  import aa                     import aa                    |     import aa
  Enum[aa]([                    ETest = Enum[aa]([           |     Enum[aa, True]([                                       ETest = Enum[True]([
      "AA",                         "AA",                    |         "AA = 0x10",                                           "AA",
      "BB",                         "BB",                    |         "BB",                                                  "BB",
      "CC = 3",                     "CC = 3",                |         "CC",                                                  "CC",
      "DD",                         "DD",                    |         "DD",                                                  "DD",
      "EE = 0x1234abc",             "EE = 0b1100 1001"       |         "EE"                                                   "EE"
      ....                          ....                     |         ....                                                   ....
      ])                            ])                       |         ])                                                     ])
获取匿名枚举值：               获取命名枚举值：              |    上面的值列表为：                                       上面的值列表为：
aa.AA                          aa.BB 或：ETest.BB            |    aa.AA == 0x10; aa.BB == 0x20; aa.CC == 0x40; ...       aa.AA == 0x1; aa.BB == 0x2; aa.CC == 0x4; ...
规则：
    1、赋值必须是整数（如果不是整数，没必要使用 Enum，用 class 即可）
    2、默认第一个枚举值为 1，后面依次递增 1（可以自行指定的整形值开始）
    3、如果要指定值，排在后面的值必须要比前面的大
	4、指定值可以是十进制、十六进制、八进制、二进制
	5、为了清晰显示，每个值位之间可以插入空格（但不能插入“\t”），如上例“EE”的定义

records:
	writen by yongwei-huang -- 2009.08.10
"""

import re

class MetaEnum(type):
	def __getitem__(cls, eInfo):
		if type(eInfo) is tuple:
			assert len(eInfo) == 2, "Enum's subscript must be: Enum[module] or Enum[mudule, increase value]."
			module, binc = eInfo
		elif type(eInfo) is bool:
			class Module: pass
			module, binc = Module, eInfo
		else:
			module, binc = eInfo, False
		return cls.__initbymeta__(module, binc)

class Enum(object):
	__slots__ = ("__module", "__elemList", \
		"__tmpValue", "__tmpLastName", "__tmpLastValue", "__tmpBInc")
	__metaclass__ = MetaEnum

	__reptnItem = re.compile("^([A-z_]\w*)\s*(?:=(.+))?$")

	def __init__(self, names=None):
		if names is not None:
			class Module: pass
			self.__module = Module
			self.__elemList = []
			self.__tmpValue = 1
			self.__tmpLastValue = None
			self.__tmpBInc = False
			self.__call__(names)

	@classmethod
	def __initbymeta__(cls, module, binc):
		self = cls()
		self.__module = module
		self.__elemList = []
		self.__tmpValue = 1
		self.__tmpLastValue = None
		self.__tmpBInc = binc
		return self


	# ----------------------------------------------------------------
	# inners
	# ----------------------------------------------------------------
	def __repr__(self):
		return "Enum[%s](...)" % self.__module
	__str__ = __repr__

	def __getattr__(self, name):
		if hasattr(self.__module, name):
			return getattr(self.__module, name)
		return object.__getattribute__(self, name)

	def __getattribute__(self, name):
		return object.__getattribute__(self, name)

	def __setattr__(self, name, value):
		if name[5:] in Enum.__slots__:
			object.__setattr__(self, name, value)
		elif name in self.__elemList:
			raise TypeError("Enum object does not support item assignment.")
		else:
			raise AttributeError("Enum object %r has no attribute %r." % (self, name))

	def __getitem__(self, name):
		if name not in self.__elemList:
			raise AttributeError("Enum object %r has no attribute %r." % (self, name))
		try:
			return getattr(self.__module, name)
		except:
			raise AttributeError("Enum object %r has no attribute %r." % (self, name))

	def __iter__(self):
		return self.__elemList.__iter__()

	# -------------------------------------------------
	def __call__(self, names):
		if not hasattr(self, "_Enum__tmpValue"):
			raise TypeError("Enum object is not callable.")
		if type(names) is not list:
			raise TypeError("Error enum items assignment: %r" % names)
		for name in names:
			name, value = self.__explain(name)
			if hasattr(self.__module, name):
				raise ValueError("error take place in module %r:\nenum member '%s' is defined duplicately." % (self.__module, name))
			self.__elemList.append(name)
			value = self.__incValue(name, value)
			setattr(self.__module, name, value)
		del self.__tmpLastValue
		del self.__tmpValue
		del self.__tmpBInc
		return self

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def module(self):
		return self.__module

	@property
	def maxValue(self):
		return getattr(self.__module, self.__elemList[-1])


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __incValue(self, name, value=None):
		if value is None:
			value = self.__tmpValue
		elif self.__tmpLastValue is not None and value <= self.__tmpLastValue:
			err = "error take place in module %r:\n"
			err += "custom enum value of %r must large then the value of its brother '%s(=%i)'s value, but not %i."
			err %= (self.__module, name, self.__tmpLastName, self.__tmpLastValue, value)
			raise ValueError(err)

		self.__tmpLastName = name
		self.__tmpLastValue = value
		if self.__tmpBInc:
			self.__tmpValue = value << 1 if value != 0 else 1
		else:
			self.__tmpValue = value + 1
		return value

	def __explain(self, item):
		match = self.__reptnItem.search(item)
		if match is None:
			raise AttributeError("error enum item name %r" % item)
		name, strValue = match.groups()
		if strValue is None:
			return name, None
		strValue = re.sub("\s", "", strValue)
		try:
			value = eval(strValue)
		except Exception, err:
			raise SyntaxError("Enum item(%s):\n%s" % (item, err.message))
		if type(value) in (int, long):
			return name, value
		raise ValueError("The type of enum value must be int or long.")


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def count(self):
		return len(self.__elemList)

	def hasEnumName(self, ename):
		return ename in self.__elemList

	def hasEnumValue(self, value):
		return value in self.itervalues()

	def iteritems(self):
		for name in self.__elemList:
			yield (name, getattr(self.__module, name))

	def itervalues(self):
		for name in self.__elemList:
			yield getattr(self.__module, name)

	def value2name(self, value):
		elist = self.__elemList
		min = 0
		max = len(elist)
		half = max / 2
		while min < max:
			name = elist[half]
			v = self[name]
			if v == value: return name
			if half == min: break
			if half == max: break
			if v > value: max = half
			else: min = half
			half = (min + max) / 2
		raise ValueError("enum %r is not contain enum member which value is %i" % (self, value))

