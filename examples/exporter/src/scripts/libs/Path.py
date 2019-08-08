# -*- coding: utf-8 -*-
#

"""
2011.09.20: writen by hyw
"""

import os
import sys
import inspect
from encode import script2sys
from encode import sys2script

def getBaseName(filePath):
	"""
	获取文件路径中的不带扩展名的文件名
	"""
	return sys2script(os.path.splitext(os.path.basename(path))[0])

def normalizePath(path):
	"""
	正规化一个路径
	如：D:/sdff///sdf\sdf/sdf/../../dfdf.h 正规化后为：
		D:\sdff\sdf\dfdf.h
	"""
	if path == "": return ""
	path = path.replace("\\", "/")
	while True:
		tmp = path.replace("//", "/")
		if tmp == path: break
		path = tmp
	folders = path.split("/")
	lfolders = []
	for f in folders:
		if f == ".." and len(lfolders):
			lfolders.pop()
		elif f != ".":
			lfolders.append(f)
	return os.path.sep.join(lfolders)

def isSamePath(path1, path2):
	"""
	判断两个路径是否相同
	"""
	path1 = os.path.realpath(path1)
	path2 = os.path.realpath(path2)
	return path1 == path2

def isRootPath(root, sub):
	"""
	判定某路径是否是另一个路径的根路径
	"""
	root = os.path.realpath(root)
	sub = os.path.realpath(sub)
	return sub.startswith(root);

def cutRoot(root, path):
	"""
	截断指定路径的根
	"""
	root = os.path.realpath(root)
	path = os.path.realpath(path)
	return path[len(root)+1:]

# --------------------------------------------------------------------
def createPath(path):
	"""
	创建路径
	"""
	if path.strip() == "":
		return False
	path = script2sys(path)
	path = normalizePath(path)
	dirs = path.split(os.path.sep)
	root = ""
	while len(dirs):
		root = os.path.join(root, dirs.pop(0)) + os.path.sep
		if not (os.path.exists(root)):
			os.mkdir(root)
	return True

# --------------------------------------------------------------------
def executeDirectory():
	"""
	获取当前路径
	"""
	path = os.path.realpath(sys.path[0])								# interpreter starter's path
	if os.path.isfile(path):												# starter is excutable file
		path = os.path.dirname(path)
		currPath = os.path.abspath(path)								# return excutable file's directory
	else:																# starter is python script
		caller_file = inspect.stack()[1][1]								# function caller's filename
		currPath = os.path.abspath(os.path.dirname(caller_file))		# return function caller's file's directory
	return sys2script(currPath)

def realToExecutePath(rpath):
	"""
	给出一个相对可执行程序所在路径的相对路径，获取其绝对路径
	如果传入一个绝对路径，则只对该路径正规化后返回
	"""
	return normalizePath(os.path.join(executeDirectory(), rpath))


# --------------------------------------------------------------------
def changeExtention(file, ext):
	"""
	修改文件扩展名
	"""
	if not ext.startswith("."):
		ext = "." + ext
	return os.path.splitext(file)[0] + ext
