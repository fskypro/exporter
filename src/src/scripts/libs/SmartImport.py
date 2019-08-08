# -*- coding: utf-8 -*-
#

"""
自已的模块导入函数，在所有的服务器端都有可能被调用；
以后如果整合全局函数的时候要把这个放进去，现在没地方放只好先放了。

records:
	1、wirten：
		by yongwei-huang -- 2010/08/17
	2、modified：
		1) rewrite 'smartImport'
		2) modified 'importAll' to support files in common
		by yongwei-huang -- 2013/01/24
"""

import os
import re
import sys
import glob

# --------------------------------------------------------------------
# inners
# --------------------------------------------------------------------
EVN_PATHS = []
_PY_EXTS = set([".py", ".pyc", ".pyd", ".po"])


def _isPathExists(path):
	"""
	判断路径是否存在
	"""
	return os.path.exists(path)					# 不能用此判断，因为脚本路径是配出来的

def _iterFiles(path, filter):
	"""
	列出指定路径下所有文件
	"""
	for fileName in glob.glob1(filePath, filter):
		yield fileName

# --------------------------------------------------------------------
def dynImport(mname):
	"""
	动态导入一个模块
	@type			mname		: STRING
	@param			mname		: 模块名称。具体格式为"mod1.mod2.modN:member"
	@rtype				 		: module
	@return				 		: 返回指定的模块
	@exception					: 如果模块不存在则抛出 ImportError 异常
								  如果冒号后的成员不存在，则抛出 AttributeError 异常
	"""
	mInfos = mname.split(":")
	module = mInfos[0]
	module = __import__(module, globals(), locals(), [module])
	if len(mInfos) == 1: return module
	return getattr(module, mInfos[1])

def smartImport(mname):
	"""
	导入一个模块。
	@type			mname		: STRING
	@param			mname		: 模块名称。具体格式为"mod1.mod2.modN:className"
								  其中":className"是可选的，表示要导入哪个类，如果存在则只允许有一个，类似于 "from mod import className"
								  也就是说可以直接导入一个模块里指定的类。
	@rtype				 		: module or an class in module
	@return				 		: 返回指定的模块或在模块中的类（如果指定的话）
	@raise 			ImportError : 如果指定的模块不存在，则产生此异常：ImportError
								: 如果指定的模块存在，但模块中的类不存在，则产生异常：AttributeError
	"""
	ms = mname.split(":")
	assert len(ms) < 3, "wrong module name: %s!" % mname				# 排除空路径
	try:
		mod = __import__(ms[0])
	except ImportError, err:
		sys.excepthook(ImportError, err, sys.exc_info()[2])
		raise ImportError("module path '%s' is not exist! err:%s" % (mname, err))
	if len(ms) == 1:
		return sys.modules[ms[0]]
	return getattr(sys.modules[ms[0]], ms[1])


def importAll(modulePath, filter="*"):
	"""
	import 指定文件夹下的所有模块
	@type			modulePath: str
	@param			modulePath: 要 import 的路径（必须为 script 下的路径，如："common/Lib"、"client/quest"）
	@type			filter    : str
	@param			filter    : 过滤器（如："plugin_*" 表示加载以 "plugin" 开头的所有模块）
	@type					  : list
	@return					  : 指定文件夹下的所有模块
	@raise 			IOError   : 如果指定的路径不存在，则抛出该异常
	"""
	path = re.sub(r"(?:\\+)|(?:/+)", "/", modulePath)
	if path.endswith("/"): path = path[:-1]
	filePath = None
	for root in EVN_PATHS:
		fullPath = os.path.join(root, path)							# 资源全路径
		if _isPathExists(fullPath):
			filePath = fullPath
			break
	if filePath is None:
		raise IOError("No such file or directory:%s" % modulePath)

	modules = []
	fileNames = set()
	mpath = path.replace("/", ".")
	for f in _iterFiles(filePath, filter):
		name, ext = os.path.splitext(f)
		if ext not in _PY_EXTS: continue
		if name in fileNames: continue
		fileNames.add(name)
		mfile = "%s.%s" % (mpath, name)
		try:
			mod = __import__(mfile)
		except Exception, e:
			sys.excepthook(Exception, e, sys.exc_info()[2])
		else:
			modules.append(sys.modules[mfile])
	return modules
