# -*- coding: utf-8 -*-
#

"""
全局宏定义

writen by hyw -- 2014.03.18
"""

# --------------------------------------------------------------------
# macro defination
# --------------------------------------------------------------------
class KEYRET_NORMAL: pass				# onRowExported::onRowExplained 返回该值表示忽略该行，并不提示
class KEYRET_EMPTY: pass				# 键返回此值表示该行键为空
class KEYRET_IGNOR: pass				# 键返回此值表示该行忽略（不导出）
class ABANDON_COL: pass					# 解释器返回 ABANDON_VALUE 表示不导出字典里的该列