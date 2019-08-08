# -*- coding: utf-8 -*-
#

"""
将表格中多个列的内容，组成一个数组返回的解释器
如果其中一个元素解释器返回 ABANDON_COL 则其返回值不被作为返回列表的元素

writen by yongwei-huang -- 2013.04.12
"""

from ex_base import ex_base
from define import ABANDON_COL				# 返回此值表示字典里的该列不导出


# --------------------------------------------------------------------
# 将多个解释器的解释结果组成一个列表返回
# extras:
#	defValue 表示默认值
# --------------------------------------------------------------------
class ex_inlay_exp_list(ex_base):
	"""
	如果某个嵌套解释器返回 ABANDON_COL，则不被作为返回列表的元素
	构造函数参数 exps 为解释器列表
		返回结果是一个不定元素个数的 list
	"""
	def __init__(self, *exps, **extras):
		self.exps_ = exps
		if "defValue" in extras:
			defValue = extras.pop("defValue")
		else:
			defValue = ex_base.INNER
		ex_base.__init__(self, defValue, **extras)				# 如果最后一个参数不是解释器的话，则认为最后一个为默认值

	def __call__(self, dsrc, row):
		return self.filter_(self.getElemList_(dsrc, row))


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getElemList_(self, dsrc, row):
		"""
		以列表形式获取所有元素
		"""
		elems = []
		for f in self.exps_:
			value = f(dsrc, row)
			if value is not ABANDON_COL:
				elems.append(value)
		return elems

	def filter_(self, value=ex_base.INNER):
		"""
		如果构造函数中传入 extra 的参数带有 excludeValue 则：
			1、如果解释所有内嵌解释式的内容都为空，则返回 ABANDON_COL
			2、如果解释内容与 exclueValue 值相等，则返回 ABANDON_COL
		如果构造函数中传入的 extra 参数中没带有 excludeValue 则：
			1、如果解释内容为空，同时传入了 defValue，则返回 defValue
			2、如果解释内容为空，但没传入 defValue，则返回空列表
		"""
		if value is ex_base.INNER:									# 解释内容为空
			if self.isExcludeValue_():								# 有排除值
				return ABANDON_COL
			elif self.defValue_ is ex_base.INNER:					# 没有传入默认值
				return self.fnRet([])
			return self.fnRet(self.defValue_)						# 有默认值
		elif self.isExcludeValue_(value):							# 解释内容与排除值相等
			return ABANDON_COL
		return self.fnRet(value)


# --------------------------------------------------------------------
# 将多个解释器的解释结果组成一个元组返回
# --------------------------------------------------------------------
class ex_inlay_exp_tuple(ex_inlay_exp_list):
	"""
	将多个解释器的解释结果组成一个元组返回
	如果某个嵌套解释器返回 ABANDON_COL，则不被作为返回元组的元素
	构造函数参数 exps 为解释器列表
		返回结果是一个不定元素个数的 tuple
	"""
	def __call__(self, dsrc, row):
		value = self.getElemList_(dsrc, row)
		return self.filter_(tuple(value))


# --------------------------------------------------------------------
# 将多个解释器的解释结果组成一个集合返回
# --------------------------------------------------------------------
class ex_inlay_exp_set(ex_inlay_exp_list):
	"""
	将多个解释器的解释结果组成一个集合返回
	如果某个嵌套解释器返回 ABANDON_COL，则不被作为返回元组的元素
	构造函数参数 exps 为解释器列表
		返回结果是一个不定元素个数的 set
	"""
	def __call__(self, dsrc, row):
		value = self.getElemList_(dsrc, row)
		return self.filter_(set(value))


# --------------------------------------------------------------------
# 将多个解释器的解释结果组成一个冻结集合返回
# --------------------------------------------------------------------
class ex_inlay_exp_frozenset(ex_inlay_exp_list):
	"""
	将多个解释器的解释结果组成一个冻结集合返回
	如果某个嵌套解释器返回 ABANDON_COL，则不被作为返回元组的元素
	构造函数参数 exps 为解释器列表
		返回结果是一个不定元素个数的 frozenset
	"""
	def __call__(self, dsrc, row):
		value = self.getElemList_(dsrc, row)
		return self.filter_(frozenset(value))
