# -*- coding: utf-8 -*-
#

"""
基础模板

2011.09.20: writen by hyw
"""

import re
from TableExporter import *

def fmtWriteOutValue(value):
	"""
	将一个任意类型的值，格式化为导出字符串
	"""
	if isinstance(value, basestring):
		value = "\"%s\"" % re.sub(r'(?<=[^\\])"', r"\"", value)
	else:
		value = value.__repr__()
	return value

def listDefValueCodeByExcludeValue(attrDict, name, dExtra=None):
	"""
	将导出表达式中所有属性的默认值组织为一个字典：{属性名: 默认值}，并以字符串代码的形式返回
	"""
	text = "%s = {\n" % name
	for key, exp in attrDict.iteritems():
		defValue = exp.excludeValue
		if defValue is ex_base.INNER: continue
		text += "\t%s: %s,\n" % (fmtWriteOutValue(key), fmtWriteOutValue(defValue))
	if dExtra is not None and len(dExtra):
		text += "\n\t# extra defaults\n"
		for name, value in dExtra.iteritems():
			text += "\t%s: %s,\n" % (fmtWriteOutValue(name), fmtWriteOutValue(value))
	text += "\t}\n"
	return text

def listDefValueCodeByUserData(attrDict, name, dExtra=None):
	"""
	将导出表达式中所有属性的默认值组织为一个字典：{属性名: 默认值}，并以字符串代码的形式返回
	"""
	text = "%s = {\n" % name
	for key, exp in attrDict.iteritems():
		defValue = exp.userData
		if defValue is ex_base.INNER: continue
		text += "\t%s: %s,\n" % (fmtWriteOutValue(key), fmtWriteOutValue(defValue))
	if dExtra is not None and len(dExtra):
		text += "\n\t# extra defaults\n"
		for name, value in dExtra.iteritems():
			text += "\t%s: %s,\n" % (fmtWriteOutValue(name), fmtWriteOutValue(value))
	text += "\t}\n"
	return text

def createSimpleClass(clsName, attrs):
	"""
	创建一个可以被导出识别的简单类
	"""
	slots = "', '".join(attrs)
	args = ", ".join(attrs)
	mems = "\n".join("\t\tself.%s = %s" % (n, n) for n in attrs)
	clsCode = """
class %(name)s(object):
	__slots__ = ['%(slots)s']
	def __init__(self, %(args)s):
%(mems)s
""" % {"name": clsName, "slots": slots, "args": args, "mems": mems}

	class SimpleClass(CustomType):
		__attrs__ = attrs
		__code__ = clsCode.strip()
		def __init__(self, *args):
			count = len(args)
			for i, n in enumerate(self.__attrs__):
				if i < count:
					setattr(self, n, args[i])
				else:
					setattr(self, n, None)

		def __repr__(self):
			clsName = self.__class__.__name__
			strValues = ", ".join(fmtWriteOutValue(getattr(self, a)) for a in self.__attrs__)
			return "%(clsName)s(%(values)s)" % {"clsName": clsName, "values": strValues}
		__str__ = __repr__

		def orderValues(self):
			return [getattr(self, n) for n in self.__attrs__]

		def orderUpdate(self, *args):
			count = len(args)
			for i, n in enumerate(self.__attrs__):
				if i < count:
					setattr(self, n, args[i])
	SimpleClass.__name__ = clsName
	return SimpleClass
