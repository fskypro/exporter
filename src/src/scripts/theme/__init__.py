# -*- coding: utf-8 -*-
#

"""
该模块向导出模板公开指定接口
"""

# --------------------------------------------------------------------
# libs.Console
# --------------------------------------------------------------------
# 消息框按钮选项
from libs.Console import Console								# 当前控制台，通过 Console.inst() 取得控制台实例

from libs.Console import MB_OK									# 确定
from libs.Console import MB_OKCANCEL							# 确定，取消
from libs.Console import MB_ABORTRETRYIGNOR						# 终止，重试，忽略
from libs.Console import MB_YESNOCANCEL							# 是，否，取消
from libs.Console import MB_YESNO								# 是，否
from libs.Console import MB_RETRYCANCEL							# 重试，取消
from libs.Console import MB_CANCELTRYAGAINCONTINUE				# 取消，再试一次，继续(注：Windows NT下不支持)

# 消息框图标
from libs.Console import MB_ICONSTOP							# 禁止号 X
from libs.Console import MB_ICONQUESTION						# 问号
from libs.Console import MB_ICONEXCLAMATION						# 警告号
from libs.Console import MB_ICONINFORMATION						# 感叹号 i

# 消息框返回值
from libs.Console import ID_OK									# 确定
from libs.Console import ID_CANCEL								# 取消
from libs.Console import ID_ABORT								# 终止
from libs.Console import ID_RETRY								# 重试
from libs.Console import ID_IGNOR								# 忽略
from libs.Console import ID_YES									# 是
from libs.Console import ID_NO									# 否
from libs.Console import ID_TRYAGAIN							# 再试一次
from libs.Console import ID_CONTINUE							# 继续

from TextEncoder import script2sys
from libs.Console import messageBox as MessageBox
def messageBox(msg, title="", nType=MB_OK, nIcon=MB_ICONINFORMATION):
	return messageBox(msg, title, nType, nIcon)
