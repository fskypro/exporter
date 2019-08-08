# -*- coding: utf-8 -*-
#

"""
文本编码器

2011.09.20: writen by hyw
"""

import libs.encode
from config.Local import Local
from config.SysConfig import SysConfig
from Exceptions import BaseException

SCRIPT_ENCODING = "utf-8"		# 本程序使用的编码
libs.encode.g_scriptencoding = SCRIPT_ENCODING
libs.encode.g_sysencoding = "gbk"

# --------------------------------------------------------------------
# 编码转换异常
# --------------------------------------------------------------------
class EncodingException(BaseException):
	def __init__(self, tagName, **args):
		title = Local().formatLocalText("encoding", "errTitle")
		msg = Local().formatLocalText("encoding", tagName, **args)
		BaseException.__init__(self, title, msg)


# --------------------------------------------------------------------
# inner methods
# --------------------------------------------------------------------
def _convert(text, methodName, src, dst):
	if src == dst:
		return text
	if src == "ascii":
		try:
			return text.encode(dst)
		except:
			raise EncodingException("errConvert", x2x="%s: %s->%s" % (methodName, src, dst))
	elif dst == "ascii":
		try:
			return text.decode(src)
		except:
			raise EncodingException("errConvert", x2x="%s: %s->%s" % (methodName, src, dst))
	try:
		text = text.decode(src)
	except:
		raise EncodingException("errConvert", x2x="%s: %s->%s" % (methodName, src, "ascii"))
	else:
		try:
			return text.encode(dst)
		except:
			raise EncodingException("errConvert", x2x="%s: %s->%s" % (methodName, "ascii", dst))
	return text


# -------------------------------------------------------------------------
# 脚本编码与系统编码
# -------------------------------------------------------------------------
def script2sys(text):
	"""
	将脚本编码文本转换为系统默认编码文本
	"""
	return _convert(text, "script2sys", SCRIPT_ENCODING, SysConfig().sysEncoding)

def sys2script(text):
	"""
	将系统编码文本转换为脚本编码文本
	"""
	return _convert(text, "sys2script", SysConfig().sysEncoding, SCRIPT_ENCODING)


# -------------------------------------------------------------------------
# 脚本编码与数据源编码
# -------------------------------------------------------------------------
def script2dsrc(srcEncoding, text):
	"""
	将脚本编码文本转换为数据源编码文本
	"""
	return _convert(text, "script2dsrc", SCRIPT_ENCODING, srcEncoding)

def dsrc2script(srcEncoding, text):
	"""
	将数据源编码文本转换为脚本代码编码文本
	"""
	return _convert(text, "dsrc2script", srcEncoding, SCRIPT_ENCODING)


# -------------------------------------------------------------------------
# 脚本编码与输出 python 配置的编码
# -------------------------------------------------------------------------
def script2dst(dstEncoding, text):
	"""
	将脚本编码文本转换为导出 python 配置编码文本
	"""
	return _convert(text, "script2dst", SCRIPT_ENCODING, dstEncoding)

def dst2script(dstEncoding, text):
	"""
	将导出 python 配置编码文本转换为脚本编码文本
	"""
	return _convert(text, "dst2script", dstEncoding, SCRIPT_ENCODING)


# -------------------------------------------------------------------------
# 数据源编码与系统编码
# -------------------------------------------------------------------------
def dsrc2sys(srcEncoding, text):
	"""
	把 excel 编码转换为系统编码
	"""
	return _convert(text, "dsrc2sys", srcEncoding, SysConfig().sysEncoding)

def sys2dsrc(srcEncoding, text):
	"""
	将系统编码转换为 xcel 编码
	"""
	return _convert(text, "sys2dsrc", SysConfig().sysEncoding, srcEncoding)


# -------------------------------------------------------------------------
# ASCII 编码与系统默认编码
# -------------------------------------------------------------------------
def ascii2sys(text):
	"""
	将 ASCII 编码文本转换为系统默认编码文本
	注意: type(text) == types.UnicodeType 则 text 为 ansii 编码
	"""
	return _convert(text, "ascii2sys", "ascii", SysConfig().sysEncoding)

def sys2ascii(text):
	"""
	将系统默认编码转换为 ASCII
	"""
	return _convert(text, "sys2ascii", SysConfig().sysEncoding, "ascii")
