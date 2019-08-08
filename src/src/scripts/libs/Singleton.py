# -*- coding: utf-8 -*-
#

"""
实现单件

records:
	writen by yongwei-huang -- 2009.08.10
"""


# --------------------------------------------------------------------
# 单例类型类
# 该程序实现了单例类的类，在类的类中控制类对象的生成方式，
# 从而将设计模式中的单件实现，由过去的约定方式修改为技术上的支持。
# --------------------------------------------------------------------
class MetaSingletonClass(type):
	def __init__(cls, name, bases, dict):
		super(MetaSingletonClass, cls).__init__(name, bases, dict)
		cls.__inst = None
		cls.__initer = cls.__init__
		cls.__new__ = staticmethod(MetaSingletonClass.__replace_new)


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __replace_init(inst, *args, **kwds):
		"""
		替换构造 init
		"""
		pass

	@staticmethod
	def __replace_new(cls, *args, **kwds):
		"""
		新的替换 new
		"""
		if cls.__inst is None:
			cls.__inst = object.__new__(cls)
			cls.__init__(cls.__inst, *args, **kwds)
			cls.__init__ = MetaSingletonClass.__replace_init
		return cls.__inst

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def insted(cls):
		"""
		是否已经初始化了单件实例
		"""
		return cls.__inst is not None

	def inst(cls):
		"""
		获取单件实例
		"""
		return cls()

	def releaseInst(cls):
		"""
		释放掉当前实例
		"""
		cls.__inst = None
		cls.__init__ = cls.__initer


# -----------------------------------------------------
# 单例基类，如果某个类继承于 Singleton，则该类将会自动成为单例类
# -----------------------------------------------------
class Singleton(object):
	__slots__ = ()
	__metaclass__ = MetaSingletonClass

	def clsName(self):
		return self.__class__.__name__
