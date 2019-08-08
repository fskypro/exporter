# -*- coding: utf-8 -*-
#

"""
实现一些通用装饰器

records:
	writen by yongwei-huang -- 2013.05.31
"""

# --------------------------------------------------------------------
# 调用列表装饰器
# --------------------------------------------------------------------
def caller_in_list(callers):
	def deco(func):
		callers.append(func)
	return deco

def caller_in_dict(callers, *keys):
	def deco(func):
		for key in keys:
			if key in callers:
				raise KeyError("caller key %r has been exist." % key)
			callers[key] = func
		return func
	return deco
