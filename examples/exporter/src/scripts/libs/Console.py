# -*- coding: utf-8 -*-
#

"""
控制台管理器
"""

import ctypes
import win32api
from encode import script2sys
from encode import sys2script

kernel32 = ctypes.windll.kernel32

# --------------------------------------------------------------------
# MACRO
# --------------------------------------------------------------------
class COORD(ctypes.Structure):
	_fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
	def __init__(self, x=0, y=0):
		self.X = x
		self.Y = y

class SMALL_RECT(ctypes.Structure):
	_fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short), ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
	_fields_ = [("Size", COORD), ("CursorPosition", COORD), ("Attributes", ctypes.c_short), \
		("Window", SMALL_RECT), ("MaximumWindowSize", COORD)]


# --------------------------------------------------------------------
# implement console class
# --------------------------------------------------------------------
class Console(object):
	__inst = None
	STD_OUTPUT_HANDLE	= -11							# 控制台

	def __init__(self):
		assert Console.__inst is None
		self.__hDevice = kernel32.GetStdHandle(Console.STD_OUTPUT_HANDLE)	# 控制台设备句柄
		self.__title = win32api.GetConsoleTitle()				# cmd 窗口标题

	@staticmethod
	def inst():
		if Console.__inst is None:
			Console.__inst = Console()
		return Console.__inst

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def hWnd(self):
		"""
		控制台窗口句柄
		"""
		# -----------------------------------
		# 通过 win32ui 获取窗口句柄
		# -----------------------------------
		win32ui = None
		try: import win32ui									# 如果完全打包，将找不到 win32ui（还不知道什么原因）
		except: pass

		hCmdWnd = -1
		if win32ui is not None:
			try:
				cmdWnd = win32ui.FindWindow(None, self.__title)
				hCmdWnd = cmdWnd.GetSafeHwnd()				# 控制台所属窗口句柄
			except:
				pass
		if hCmdWnd > 0:
			return hCmdWnd
		# -----------------------------------

		# -----------------------------------
		# 通过 winappdbg 库获取窗口句柄
		# -----------------------------------
		from winappdbg import win32
		try:
			hCmdWnd = win32.user32.FindWindowA(None, self.__title)
		except Exception, err:
			try:
				hCmdWnd = win32.user32.FindWindowW(None, self.__title)
			except:
				pass
		return hCmdWnd
		# -----------------------------------

	@property
	def title(self):
		return sys2script(self.__title)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def setCursorPos(self, x, y):
		"""
		设置光标位置
		"""
		kernel32.SetConsoleCursorPosition(self.__hDevice, COORD(x, y))

	def getCursorPos(self):
		"""
		获取光标位置
		"""
		buffer = CONSOLE_SCREEN_BUFFER_INFO()
		kernel32.GetConsoleScreenBufferInfo(self.__hDevice, ctypes.byref(buffer))
		return buffer.CursorPosition.X, buffer.CursorPosition.Y


# --------------------------------------------------------------------
# 弹出消息框
# --------------------------------------------------------------------
# 消息框按钮选项
MB_OK						= 0		# 确定
MB_OKCANCEL					= 1		# 确定，取消
MB_ABORTRETRYIGNOR			= 2		# 终止，重试，忽略
MB_YESNOCANCEL				= 3		# 是，否，取消
MB_YESNO					= 4		# 是，否
MB_RETRYCANCEL				= 5		# 重试，取消
MB_CANCELTRYAGAINCONTINUE	= 6		# 取消，再试一次，继续(注：Windows NT下不支持)

# 消息框图标
MB_ICONSTOP					= 16	# 禁止号 X
MB_ICONQUESTION				= 32	# 问号
MB_ICONEXCLAMATION			= 48	# 警告号
MB_ICONINFORMATION			= 64	# 感叹号i 值为64或者0x00000040L

# 消息框返回值
ID_OK						= 1		# 确定
ID_CANCEL					= 2		# 取消
ID_ABORT					= 3		# 终止
ID_RETRY					= 4		# 重试
ID_IGNOR					= 5		# 忽略
ID_YES						= 6		# 是
ID_NO						= 7		# 否
ID_TRYAGAIN					= 10	# 再试一次
ID_CONTINUE					= 11	# 继续

def messageBox(msg, title="", nType=MB_OK, nIcon=MB_ICONINFORMATION):
	title, msg = script2sys(title), script2sys(msg)
	return win32api.MessageBox(Console.inst().hWnd, msg, title, nType|nIcon)
