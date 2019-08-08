# -*- coding: utf-8 -*-
#

"""
控制台打印机


2011.09.20: writen by hyw
"""

from engine import Listener
from libs.Console import Console
from config.Local import Local
from config.CustomConfig import CustomConfig
from TextEncoder import script2sys

_msg_cache = []


# --------------------------------------------------------------------
# 获取语言配置中的字符串
# --------------------------------------------------------------------
def dtext(_key, _name, **args):
	"""
	提取语言配置中的文本
	"""
	return Local().formatLocalText(_key, _name, **args)

def _dsystext(_key, _name, **args):
	"""
	提取语言配置中的文本，并转换为系统编码
	"""
	return script2sys(Local().formatLocalText(_key, _name, **args))


# --------------------------------------------------------------------
# 输出文本（所有参数必需为脚本编码）
# --------------------------------------------------------------------
def dmsg(*msgs):
	"""
	打印字符串后换行
	msg 必须与 python 编码一致
	"""
	msg = ", ".join([str(m) for m in msgs])
	msg = script2sys(msg)
	if ProgressRecord.running:
		_msg_cache.append(msg)
	else:
		print msg

def catmsg(*msgs):
	"""
	打印字符串后不换行
	msg 必须与 python 编码一致
	"""
	msg = ", ".join([str(m) for m in msgs])
	msg = script2sys(msg)
	if ProgressRecord.running:
		if len(_msg_cache) and type(_msg_cache[-1]) is list:
			_msg_cache[-1].append(msg)
		else:
			_msg_cache.append([msg])
	else:
		print msg,


# --------------------------------------------------------------------
# 输出在语言配置中的文本（所有参数必需为脚本编码）
# --------------------------------------------------------------------
def dout(_key, _name, **args):
	"""
	打印语言配置中的字符串后换行
	args 如果是字符串，必须与 python 脚本编码一致
	"""
	msg = _dsystext(_key, _name, **args)
	if ProgressRecord.running:
		_msg_cache.append(msg)
	else:
		print msg

def catout(_key, _name, **args):
	"""
	打印语言配置中的字符串后不换行
	args 如果是字符串，必须与 python 脚本编码一致
	"""
	msg = _dsystext(_key, _name, **args)
	if ProgressRecord.running:
		if len(_msg_cache) and type(_msg_cache[-1]) is list:
			_msg_cache[-1].append(msg)
		else:
			_msg_cache.append([msg])
	else:
		print msg,


# ------------------------------------------------------------------------------
# 打印区块信息:
# ------------------------------------------------------------------------------
def printNewline():
	"""
	换行
	"""
	print

def printBlockSplitter():
	"""
	打印区块分割线
	"""
	print "# %s" % (CustomConfig().query("custom/blockWidth", int) * \
		CustomConfig().query("custom/blockSplitter"))

def printBlockHead(title, lines, width=None, blockChr=None):
	"""
	打印一个区块头
	"""
	if width is None:
		width = CustomConfig().query("custom/blockWidth", int)
	if blockChr is None:
		blockChr = CustomConfig().query("custom/blockSplitter")
	splitter = blockChr * width
	print "# %s" % splitter
	if title is not None:
		print "# %s" % script2sys(title)
		print "# %s" % ('-' * width)
	for line in lines:
		print "# %s" % script2sys(line)
	print "# %s" % splitter


# ------------------------------------------------------------------------------
# 打印进度
# ------------------------------------------------------------------------------
def _flushCacheMsg():
	global _msg_cache
	for msg in _msg_cache:
		if type(msg) is list:
			for m in msg:
				print m,
		else:
			print msg
	_msg_cache = []


class ProgressRecord:
	cx = cy = 0
	progress = 0.0
	running = False
	printer = None
	@classmethod
	def clear(cls):
		cls.cx = cls.cy = 0
		cls.running = False
		cls.printer = None
		_flushCacheMsg()


# --------------------------------------------------------------------
# 锁住打印机，并返回一个支持光标在同一个起始位置循环打印的函数
# --------------------------------------------------------------------
def capPrinter(isMsgCap, cacheLen=50):
	"""
	返回一个函数，cacheLen 为缓冲长度
	"""
	assert not ProgressRecord.running, "a progress printer has been capped."
	ProgressRecord.cx, ProgressRecord.cy = Console.inst().getCursorPos()
	ProgressRecord.running = True

	fmt = "%%-%is" % cacheLen
	class CapPrinter(object):
		if isMsgCap:
			def __call__(self, msg):							# msg 编码必须与 python 脚本编码一致
				cx = ProgressRecord.cx
				cy = ProgressRecord.cy
				Console.inst().setCursorPos(cx, cy)
				print fmt % script2sys(msg)
		else:
			def __call__(self, _key, _name, **args):
				cx = ProgressRecord.cx
				cy = ProgressRecord.cy
				Console.inst().setCursorPos(cx, cy)
				print fmt % _dsystext(_key, _name, **args)
	ProgressRecord.printer = CapPrinter()
	return ProgressRecord.printer

def uncapPrinter(cappedPrinter=None):
	"""
	解锁打印机
	"""
	if cappedPrinter is None or cappedPrinter == ProgressRecord.printer:
		ProgressRecord.clear()
		return True
	return False

def isPrinterCapped():
	"""
	指出打印机是否被锁
	"""
	return ProgressRecord.running


# --------------------------------------------------------------------
# exit callback
# --------------------------------------------------------------------
def onAppExit(exitCode):
	"""
	程序退出时，解锁打印机
	"""
	uncapPrinter()
Listener().cbAppExit.bind(onAppExit)
