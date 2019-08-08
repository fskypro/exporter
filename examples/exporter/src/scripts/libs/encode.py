# -*- coding: utf-8 -*-
#

"""
编码定义
2018.03.07: writen by hyw
"""

g_scriptencoding = "utf8"				# 脚本编码
g_sysencoding      = "gbk"				# 系统编码

def script2sys(text):
	"""
	脚本编码转换为系统编码
	"""
	if (g_scriptencoding != g_sysencoding):
		return text.decode(g_scriptencoding).encode(g_sysencoding)
	return text

def sys2script(text):
	"""
	系统编码转换为脚本编码
	"""
	if (g_scriptencoding != g_sysencoding):
		return text.decode(g_sysencoding).encode(g_scriptencoding)
	return text
