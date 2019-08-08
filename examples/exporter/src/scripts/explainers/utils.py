# -*- coding: utf-8 -*-
#

"""
record:
	writen by yongwei-huang -- 2014.04.24
"""


def splits(text, sps):
	"""
	将文本 text 以一组分隔符拆分成一组文本列表
	"""
	if len(text) == 0:
		return ['']
	subs = []
	sub = ""
	while len(text):
		cutted, text = cutStarts(text, sps)
		if cutted:
			subs.append(sub)
			sub = ""
		else:
			sub += text[0]
			text = text[1:]
	if len(sub):
		subs.append(sub)
	return subs

def contains(text, chs):
	"""
	文本中，是否至少存在指定列表中列出的一组字符
	"""
	for ch in chs:
		if ch in text:
			return True
	return False

def startsWiths(text, chs):
	"""
	判断给定的字符串是否以给出的一组字符开头
	"""
	for ch in chs:
		if text.startswith(ch):
			return True
	return False

def endsWiths(text, chs):
	"""
	判断给定的字符串是否以给出的一组字符结束
	"""
	for ch in chs:
		if text.endswith(ch):
			return True
	return False

def cutStarts(text, chs):
	"""
	截去文本中以 chs 开头的字符
	如果有需要被截去的字符，则返回（True, 剩余的字符串）
	如果没有需要被截的字符，则返回（False，原来的字符串）
	"""
	for ch in chs:
		if text.startswith(ch):
			return True, text[len(ch):]
	return False, text

def cutEnds(text, chs):
	"""
	截去文本中以 chs 结尾的字符
	如果有需要被截去的字符，则返回（True, 剩余的字符串）
	如果没有需要被截的字符，则返回（False，原来的字符串）
	"""
	for ch in chs:
		if text.endswith(ch):
			return True, text[:-len(ch)]
	return False, text

def findScopes(text, starts, ends):
	"""
	查找字符串中，以一组字符开头，和一组字符结尾的所有子字符串组
	"""
	subs = []
	sub = ""
	state = 0												# 0 为未开始；1 为开始；2 为结束
	while len(text):
		if state == 1:										# 搜寻结束符
			cutted, text = cutStarts(text, ends)
			if cutted:										# 找到结束符
				state = 2									# 标记为结束
				subs.append(sub)
				sub = ""
				continue
		else:												# 搜寻起始符
			cutted, text = cutStarts(text, starts)
			if cutted:										# 找到起始符
				state = 1									# 标记为起始
				continue
		if state == 1:
			sub += text[0]
		text = text[1:]
	return subs
