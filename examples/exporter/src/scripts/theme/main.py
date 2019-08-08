# -*- coding: utf-8 -*-
#

"""
2011.09.20: writen by hyw
"""

import os
import sys
import inspect
import __builtin__
import engine
import TextEncoder
from libs import Path
from libs.Console import messageBox
from libs.Console import MB_OK
from libs.Console import MB_ICONSTOP
from TextEncoder import sys2script
from TextEncoder import script2sys
from config.Local import Local
from config.CustomConfig import CustomConfig
from Exceptions import BaseException
from engine import Listener
from exporter import exporter
from theme import Printer

# 是否为 debug 版本
def _isDebug():
	return getattr(__builtin__, "__GB_DEBUG__", False)

# --------------------------------------------------------------------
# 初始化导出模板
# --------------------------------------------------------------------
def _printAppMsg():
	"""
	打印程序信息
	"""
	Printer.printBlockHead(
		Printer.dtext("theme", "tipsProgramInfo"),
		["program: TableExporter.exe",
		"version: %s" % engine.VERSION,
		"author : huangyongwei",
		"date   : 2011/09/20", ],)

def _printTplMsg(tplFileName):
	"""
	打印模板信息
	"""
	Printer.printNewline()
	Printer.printBlockHead(None, [Printer.dtext("theme", "tipsTplFile", file=tplFileName)])

# -----------------------------------------------------
def _initEnvironment():
	"""
	初始化环境变量
	"""
	sys.path.append(script2sys(Path.executeDirectory()))				# 将程序根目录添加到环境变量
	for root in CustomConfig().syscodeTplRoots:						# 将配置文件所在路径加入环境变量
		sys.path.append(root)
	if CustomConfig().syscodeSrcPluginRoot != "":
		sys.path.append(CustomConfig().syscodeSrcPluginRoot)		# 数据源插件根目录
	if CustomConfig().syscodeDstPluginRoot != "":
		sys.path.append(CustomConfig().syscodeDstPluginRoot)		# 数据导出插件根目录

def _initExportTpl(tplFile):
	"""
	初始化导出模板
	"""
	exists = False
	for root in CustomConfig().tplRoots:
		fullName = os.path.join(root, tplFile)
		if os.path.exists(script2sys(fullName)):
			exists = True
			break
	if not exists:
		Printer.dout("theme", "errTplFileUnxist", tpl=tplFile)
		engine.exit(1)
	else:
		_printTplMsg(fullName)

	tplFile = os.path.splitext(tplFile)[0]
	tplFile = tplFile.replace("\\", ".").replace("/", ".")
	try:
		tplFile = script2sys(tplFile)
		tplModule = __import__(tplFile, globals(), locals(), [tplFile])		# 导出模板
		return tplModule
	except BaseException, err:
		if not _isDebug(): print err.sysMsg
		else: sys.excepthook(BaseException, err, sys.exc_traceback)
		messageBox(err.scriptMsg, "ERROR", MB_OK, MB_ICONSTOP)
	except Exception, err:
		sys.excepthook(Exception, err, sys.exc_traceback)
	engine.exit(1)


# --------------------------------------------------------------------
# callbacks
# --------------------------------------------------------------------
def onInfo(msg):
	"""
	提示信息回调
	"""
	Printer.dmsg("Info: %s" % msg)
Listener().cbInfo.bind(onInfo)

def onWarning(msg):
	"""
	警告信息回调
	"""
	Printer.dmsg("Warning: %s" % msg)
Listener().cbWarning.bind(onWarning)

def onError(msg):
	"""
	错误信息回调
	"""
	Printer.dmsg("Error: %s" % msg)
Listener().cbError.bind(onError)

def onLocalMsg(key, tag, **attrs):
	"""
	语言配置中信息回调
	"""
	Printer.dout(key, tag, **attrs)
Listener().cbLocalMsg.bind(onLocalMsg)

# -----------------------------------------------------
_cappedPrint = None

def onBeginLoadDataSource(loadTracer):
	"""
	开始加载数据源时被调用
	"""
	Printer.dout("theme", "tipsLoadDataSource", src=loadTracer.getSrcText())
	if CustomConfig().query("custom/showProgress", bool):
		global _cappedPrint
		_cappedPrint = Printer.capPrinter(True)
		pbarLen = CustomConfig().query("custom/pbarLen", int)
		_cappedPrint.pbarLen = pbarLen
		_cappedPrint.pbarChr = CustomConfig().query("custom/pbarChar")
		_cappedPrint.fmt = Printer.dtext("theme", "tipsLoadDataSourceProgress", pbarLen=pbarLen)
Listener().cbBeginLoadDataSource.bind(onBeginLoadDataSource)

def onLoadingDataSource(loadTracer, progress):
	"""
	加载数据源进度回调
	"""
	if _cappedPrint is None: return
	passed = int(_cappedPrint.pbarLen * progress)
	_cappedPrint(_cappedPrint.fmt % {"pbar": _cappedPrint.pbarChr * passed})
Listener().cbLoadingDataSource.bind(onLoadingDataSource)

def onEndLoadDataSource(loadTracer):
	"""
	数据源加载结束后调用
	"""
	Printer.uncapPrinter()
	global _cappedPrint
	_cappedPrint = None
Listener().cbEndLoadDataSource.bind(onEndLoadDataSource)

# -----------------------------------------------------
def onBeginExport(tplModule):
	"""
	开始导出时调用
	"""
	pass
Listener().cbBeginExport.bind(onBeginExport)

# -----------------------------------------------------
def onBeginExportConfig(exportTracer):
	"""
	开始导出一个模板中的其中一个配置
	"""
	# 数据源信息
	outInfo = exportTracer.outInfo
	srcMsgs = [Printer.dtext("export", "tipsSrcData")]
	for outItemInfo in outInfo.outItemInfos:
		for text in outItemInfo.dsrcTextList:
			text = "  " + text
			if text not in srcMsgs:
				srcMsgs.append(text)
	# 导出配置信息
	dstMsgs = [Printer.dtext("export", "tipsDstFile", file=outInfo.dstFile)]

	Printer.printNewline()
	Printer.printBlockHead(Printer.dtext("export", "tipsExporedInfo"), srcMsgs+dstMsgs)
Listener().cbBeginExportOutInfo.bind(onBeginExportConfig)

_firstScanData = True
def onBeginExportConfigItem(exportItemTracer):
	"""
	开始导出一个配置选项时调用
	"""
	global _firstScanData
	_firstScanData = True
	exportTracer = exportItemTracer.owner
	if len(exportTracer.exportItemTracers) > 1:
		outItemInfo = exportItemTracer.outItemInfo
		Printer.printBlockHead(None, [Printer.dtext("theme", "tipsBeginExportItem", dname=outItemInfo.name)],
		width=CustomConfig().query("custom/blockWidth", int)-10, blockChr="-")
Listener().cbBeginExportOutItemInfo.bind(onBeginExportConfigItem)

def onBeginScanDataSource(dsrcTracer):
	"""
	开始扫描数据源
	"""
	global _firstScanData
	if _firstScanData:
		_firstScanData = False
	else:
		Printer.printNewline()

	srcText = dsrcTracer.dsrc.getSrcText()
	Printer.dout("export", "tipsScanSrcData", path=srcText)
	if CustomConfig().query("custom/showProgress", bool):
		global _cappedPrint
		_cappedPrint = Printer.capPrinter(False)
Listener().cbBeginScanDataSource.bind(onBeginScanDataSource)

def onScanningDataSource(dsrcTracer, row):
	"""
	扫描数据源进度回调
	"""
	if _cappedPrint is None: return
	rowCount = dsrcTracer.dsrc.rowCount
	if rowCount > 0:
		passed = row + 1
		percent = float(passed) / rowCount * 100
	else:
		passed = 0
		percent = 0.0
	_cappedPrint("theme", "tipsProgress", passed=passed, rows=rowCount, percent=percent)
Listener().cbScanningDataSource.bind(onScanningDataSource)

def onEndScanDataSource(dsrcTracer):
	"""
	结束一个数据源的扫描
	"""
	if CustomConfig().query("custom/showProgress", bool):
		Printer.uncapPrinter()
		global _cappedPrint
		_cappedPrint = None

	# 打印空行（键）
	if len(dsrcTracer.emptyRows):
		Printer.printNewline()
		Printer.dout("export", "warnEmptyRows", rows=dsrcTracer.emptyRows)
Listener().cbEndScanDataSource.bind(onEndScanDataSource)

def onBeginWriteConfigItem(writeTracer):
	"""
	写入配置选项
	"""
	Printer.printNewline()
	name = writeTracer.owner.outItemInfo.name
	Printer.dout("export", "tipsWriteOut", name=name)
	if CustomConfig().query("custom/showProgress", bool):
		global _cappedPrint
		_cappedPrint = Printer.capPrinter(False)
Listener().cbBeginWriteOutItemInfo.bind(onBeginWriteConfigItem)

def onWritingOutItem(writeTracer, index):
	"""
	写入配置选项进度回调
	"""
	if _cappedPrint is None: return
	count = len(writeTracer.datas)
	if count == 0:
		passed = 0
		percent = 0.0
	else:
		passed = index + 1
		percent = float(passed) / count * 100
	_cappedPrint("theme", "tipsProgress", passed=passed, rows=count, percent=percent)
Listener().cbWritingOutItemInfo.bind(onWritingOutItem)

def onEndWriteOutItem(writeTracer):
	"""
	结束一个数据源的扫描
	"""
	if CustomConfig().query("custom/showProgress", bool): Printer.uncapPrinter()
Listener().cbEndWriteOutItemInfo.bind(onEndWriteOutItem)

def onEndExportConfigItem(exportItemTracer):
	"""
	结束一个配置的导出
	"""
	# 打印重复键
	if len(exportItemTracer.dbKeys):
		Printer.printNewline()
		s = ""
		for key, count in exportItemTracer.dbKeys.iteritems():
			s += "[%s(%i)] " % (key, count)
		Printer.dout("export", "warnDBKey", keys=s)

	# 打印记录数
	Printer.printNewline()
	Printer.dout("export", "tipsRowCount", count=exportItemTracer.outItemInfo.rowCount)		# 记录总数
	Printer.dout("export", "tipsEmptyRowCount", count=exportItemTracer.emptyCount)			# 空行数（包括空键）
	Printer.dout("export", "tipsDBRowCount", count=len(exportItemTracer.dbKeys))				# 重复键的行数
	Printer.dout("export", "tipsIgnorCount", count=exportItemTracer.ignorCount)					# 忽略的行数
	Printer.dout("export", "tipsValidCount", count=len(exportItemTracer.datas))					# 有效行数

	# 打印导出时间
	writeTracer = exportItemTracer.writeTracer
	Printer.dout("theme", "tipsReadTableWaste", v=exportItemTracer.loadDSrcsTime)				# 加载数据耗时
	Printer.dout("theme", "tipsExplainWaste", v=exportItemTracer.scanDSrcsTime)					# 扫描数据耗时
	Printer.dout("theme", "tipsWriteOutWaste", v=exportItemTracer.writeTime)						# 写入配置耗时
	Printer.dout("theme", "tipsTotalWaste", v=exportItemTracer.wasteTime)						# 总耗时
	Printer.printNewline()
Listener().cbEndExportOutItemInfo.bind(onEndExportConfigItem)

# -----------------------------------------------------
def onAppExit(exitCode):
	"""
	程序退出时调用
	"""
	if exitCode == 0:
		Printer.dout("theme", "tipsExportSuccess")
	else:
		Printer.printNewline()
		Printer.dout("theme", "tipsExportFail")
Listener().cbAppExit.bind(onAppExit)


# --------------------------------------------------------------------
# entrance
# --------------------------------------------------------------------
def enter():
	"""
	argv[1]		导出模板路径
	"""
	args = sys.argv[1:]
	if len(args) < 1 or len(args[0]) == 0:
		Printer.dout("theme", "errorArgs")
		engine.exit(1)
	tplRoot = sys2script(args[0])

	# 初始化环境变量
	_initEnvironment()
	# 打印版本信息
	_printAppMsg()
	# 初始化导出模板
	tplModule = _initExportTpl(tplRoot)

	try:
		exporter.export(tplModule)
	except BaseException, err:
		if not _isDebug(): print err.sysMsg
		else: sys.excepthook(BaseException, err, sys.exc_traceback)
		messageBox(err.scriptMsg, "ERROR", MB_OK, MB_ICONSTOP)
		engine.exit(1)
	except Exception, err:
		if _isDebug():
			sys.excepthook(Exception, err, sys.exc_traceback)
		print err.args
		engine.exit(1)
	else:
		engine.exit(0)

if __name__ == "__main__":
	enter()
