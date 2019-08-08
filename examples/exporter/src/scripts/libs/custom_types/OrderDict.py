# -*- coding: utf-8 -*-
#

"""
按顺序字典
注意：非线程安全！

records:
	writen by yongwei-huang: 2013.04.10
"""

class OrderDict(dict):
	class __inner: pass

	def __init__(self, orign=()):
		dict.__init__(self, orign)
		if isinstance(orign, dict):
			self.__keys = [k for k, v in orign.iteritems()]
		else:
			self.__keys = [k for k, v in orign]


	# ----------------------------------------------------------------
	# inners
	# ----------------------------------------------------------------
	def __repr__(self):
		reprStr = "OrderDict{"
		for key in self.__keys:
			reprStr += "%r: %r, " % (key, self[key])
		if reprStr.endswith(", "):
			reprStr = reprStr[:-2]
		reprStr += "}"
		return reprStr
	__str__ = __repr__

	def __delitem__(self, key):
		dict.__delitem__(self, key)
		self.__keys.remove(key)

	def __setitem__(self, key, value):
		if key in self.__keys:
			self.__keys.remove(key)
		dict.__setitem__(self, key, value)
		self.__keys.append(key)

	def __getslice__(self, start, end):
		items = []
		for key in self.__keys.__getslice__(start, end):
			items.append((key, self[key]))
		return items

	def __iter__(self):
		return self.__keys.__iter__()

	def __contains__(self, key):
		return dict.__contains__(self, key)

	def __copy__(self):
		copy = OrderDict()
		copy.update(self)
		return copy


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def keys(self):
		return self.__keys[:]

	def values(self):
		values = []
		for key in self.__keys:
			values.append(self[key])
		return values

	def items(self):
		items = []
		for key in self.__keys:
			items.append((key, self[key]))
		return items

	# -------------------------------------------------
	def keyindex(self, key):
		try:
			return self.__keys.index(key)
		except ValueError:
			raise KeyError(key)

	def indexkey(self, index):
		return self.__keys[index]

	def indexvalue(self, index):
		return self[self.__keys[index]]

	def indexitem(self, index):
		key = self.__keys[index]
		return key, self[key]

	# -------------------------------------------------
	def iterkeys(self):
		return self.__keys.__iter__()

	def itervalues(self):
		for key in self.__keys:
			yield self[key]

	def iteritems(self):
		for key in self.__keys:
			yield (key, self[key])

	def riterkeys(self):
		for key in reversed(self.__keys):
			yield key

	def ritervalues(self):
		for key in reversed(self.__keys):
			yield self[key]

	def riteritems(self):
		for key in reversed(self.__keys):
			yield (key, self[key])

	# -------------------------------------------------
	def pop(self, key, defValue=__inner):
		if dict.__contains__(self, key):
			self.__keys.remove(key)
			return dict.pop(self, key)
		elif defValue is self.__inner:
			raise KeyError(key)
		return defValue

	def popitem(self, index=-1):
		if len(self.__keys) == 0:
			raise KeyError('popitem(): dictionary is empty')
		key = self.__keys.pop(-1)
		return key, dict.pop(self, key)

	def rmitems(self, start, end=None):
		"""
		删除指定索引起始到结束处（不包括结束索引处：[start, end)）的选项
		"""
		orignKeys = self.__keys
		if end is None:
			keys = orignKeys[start:]
			self.__keys = orignKeys[:start]
		else:
			keys = orignKeys[start:end]
			self.__keys = orignKeys[:start] + orignKeys[end:]
		items = []
		for key in keys:
			items.append((key, dict.pop(self, key)))
		return items

	def clear(self):
		dict.clear(self)
		self.__keys = []

	# -------------------------------------------------
	def setdefault(self, key, value=None):
		"""
		如果 key 存在，则返回 key 对应的值；如果不存在，则插入该值，并返回该值
		"""
		if dict.__contains__(self, key):
			return self[key]
		self[key] = value
		return value

	# -------------------------------------------------
	def topinsert(self, item, popExists=True):
		"""
		在顶部插入一个选项，popExists 表示：
			True 时，如果 key 已经存在，则删除它并在最前面插入
			False 时：如果 key 已经存在，则只更新原来的 key 对应的值
		返回插入选项的所在索引位置
		"""
		key, value = item
		index = 0
		if key in self.__keys:
			if popExists:
				self.__keys.remove(key)
				self.__keys.indert(0, key)
			else:
				index = self.__keys.index(key)
		else:
			self.__keys.insert(0, key)
		dict.__setitem__(self, key, value)
		return index

	def insert(self, index, item, popExists=True):
		"""
		在指定位置插入一个选项
			True 时，如果 key 已经存在，则删除它并在指定位置的前面添加
			False 时：如果 key 已经存在，则只更新原来的 key 对应的值
		返回新插入选项的所在索引位置
		"""
		key, value = item
		if key in self.__keys:
			if popExists:
				self.__keys.remove(key)
				self.__keys.insert(index, key)
		else:
			self.__keys.insert(index, key)
		dict.__setitem__(self, key, value)
		return self.__keys.index(key)

	def append(self, item, popExists=True):
		"""
		在末尾追加一个选项，popExists 表示：
			True 时，如果 key 已经存在，则删除它并在最后面追加
			False 时：如果 key 已经存在，则只更新原来的 key 对应的值
		返回追加选项的所在索引位置
		"""
		key, value = item
		if key in self.__keys:
			if popExists:
				self.__keys.remove(key)
				self.__keys.append(key)
				index = len(self.__keys) - 1
			else:
				index = self.__keys.index(key)
		else:
			self.__keys.append(key)
			index = len(self.__keys) - 1
		dict.__setitem__(self, key, value)
		return index

	def update(self, items):
		"""
		合并一组指定的选项，如果选项已经存在，则把原来选项删除
		"""
		if isinstance(items, dict):
			items = items.iteritems()
		for key, value in items:
			self[key] = value

	# -------------------------------------------------
	def clone(self):
		copy = OrderDict()
		copy.update(self)
		return copy

	def sort(self, comp=None, key=None, reverse=False) :
		self.__keys.sort(comp, key, reverse)
