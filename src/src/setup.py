#-*- encoding:utf-8 -*-
#

"""
Build to win32 execute file

bundle_files
1: 所有都打包成一个文件,包括python.dll
2: 把pyo,pyd都打包在一起, 不包含python.dll
3: 只打包py源程序, pyd,python.dll都单独存在
"""

import os
import sys
import glob
import py2exe
from distutils.core import setup

_mainFile = "scripts/theme/main.py"
if '-d' in sys.argv:
	sys.argv.remove('-d')
	_mainFile = "scripts/theme/main_d.py"

dlls = ["mswsock.dll", "powrprof.dll"]

sys.path.append("scripts")
includes = [
	'socket', 'TableExporter', 'explainers.ex_base',
	'win32api',
#	'win32com',
	'win32ui',
	'win32gui',
	'winappdbg']

packages = ["win32ui"]

setup(
	options = {
		"py2exe": {
			"compressed": 1,
			"optimize": 2,
			"ascii": 0,
			"bundle_files": 1,
			"dll_excludes": dlls,
			"dist_dir": "./bin",
			"includes": includes,
			"packages": packages,
			},
		},

	version = "4.0.0",
	description = "export excel datas to python dictionary config.",
	name = "TableExporter",
	company_name = "nostyle",
	copyright = "hyw",
	zipfile = None, # append zip-archive to the executable.
	# targets to build
	console = [{"script": _mainFile, "icon_resources": [(1, "./res/top.ico")]}],
	#data_files = [("aa", ["win32ui.pyd"])]
	)


# --------------------------------------------------------------------
# rename exe file
# --------------------------------------------------------------------
#import os
#os.rename(path+"/dist/main.exe", path+"/dist/excel2py.exe")
