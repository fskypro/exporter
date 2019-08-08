# -*- coding: utf-8 -*-
#

"""
该模块向导出模板公开指定接口
"""

# --------------------------------------------------------------------
# libs
# --------------------------------------------------------------------
from libs.decorators import caller_in_list						# 收集函数列表的装饰器
from libs.decorators import caller_in_dict						# 收集函数字典的装饰器
from libs.custom_types.hlint import hlint						# 十六进制整形
from libs.custom_types.xfloat import xfloat						# 可以指定取小数点后 n 位的小数
from libs.custom_types.OrderDict import OrderDict				# 有顺序的字典
from libs.custom_types.Enum import Enum							# 自定义枚举
from libs import Path											# 路径相关功能函数
from libs.PyWriter import Writer as PyWriter 					# 将 ptyon 数据写出外存的工具
from libs.SimpleXML import SXMLException						# SimpleXMLSection
from libs.SimpleXML import SimpleXML							# SimpleXML
def dynImport(mname):											# 动态加载一个模块
	from libs import SmartImport
	return SmartImport.dynImport(script2sys(mname))

# 时间扩展模块
from libs import timeex
from libs.timeex import vtime
from libs.timeex import vdate
from libs.timeex import vweek


# --------------------------------------------------------------------
# definations
# --------------------------------------------------------------------
from define import KEYRET_NORMAL								# 在 Monitor 的 onBeforeExportRow 中返回该值，表示不导出该行，但不作任何提示
from define import KEYRET_EMPTY									# 键返回此值表示该行键为空
from define import KEYRET_IGNOR									# 键返回此值表示该行忽略（不导出）
from define import ABANDON_COL									# 1、如果某解释器返回该值，则不导出该列（即字典中不会出现该列的子键）
																# 2、如果 ex_inlay_exp_tuple 的子类解释器返回该变量，则其嵌套解释器的解释结果不会被纳入 ex_inlay_exp_tuple 解释器返回的列表或元组中

# --------------------------------------------------------------------
# config
# --------------------------------------------------------------------
from config.SysConfig import SysConfig							# 系统配置，对应：bin.xml
from config.Local import Local									# 语言配置，对应：local/语言文件.xml
from config.CustomConfig import CustomConfig					# 用户配置，对应：config.xml

# --------------------------------------------------------------------
# custom exceptions
# --------------------------------------------------------------------
from Exceptions import BaseException							# 引擎的异常基类，抛出该异常导出将会被终止

from explainers.ExplainExceptions import ExplainException						# 解释数据异常，可以传入一条自定义信息，继承于 BaseException
from explainers.ExplainExceptions import ExplainFixException					# 解释数据异常，异常信息来自于local/ 下语言文件的 <explain> 键下的信息，继承于 ExplainException
from explainers.ExplainExceptions import ExplainErrorValueTypeException			# 表格数据异常，需要传入表格信息。提示信息位于语言文件下的 <explain>/<errType> 标签中

from data_srcs.DataSrcExceptions import CSVException			# 操作 csv 相关异常
from data_srcs.DataSrcExceptions import CSVFixException			# 知道明确错误的操作 CSV 相关异常
from data_srcs.DataSrcExceptions import ExcelComException		# 操作 Excel 时，Com 组件系统发出的异常
from data_srcs.DataSrcExceptions import ExcelInEditException	# 表格可能处于被编辑状态
from data_srcs.DataSrcExceptions import ExcelFixException		# 操作 Excel 时，能明确知道原因的异常


# --------------------------------------------------------------------
# TextEncoder
# --------------------------------------------------------------------
from TextEncoder import script2sys								# 将“导出模板的脚本编码”转换为“Windows 系统默认编码”
from TextEncoder import sys2script								# 将“Windows 系统默认编码”转换为“导出模板的脚本编码”

from TextEncoder import script2dsrc								# 将“导出模板的脚本编码”转换为“excel 表格采用的编码”
from TextEncoder import dsrc2script								# 将“excel 表格采用的编码”转换为“导出模板的脚本编码”

from TextEncoder import script2dst								# 将“导出模板的脚本编码”转换为“导出的 python 配置编码”
from TextEncoder import dst2script								# 将“导出的 python 配置编码”转换为“导出模板的脚本编码”

from TextEncoder import dsrc2sys								# 将“导出模板的脚本编码”转换为“Windows 系统默认编码”
from TextEncoder import sys2dsrc								# 将 “Windows 系统默认编码”转换为“导出模板的脚本编码”

from TextEncoder import ascii2sys								# 将非编码文本转换为“Windows 系统默认编码”
from TextEncoder import sys2ascii								# 将“Windows 系统默认编码”文本解码


# --------------------------------------------------------------------
# custom types
# --------------------------------------------------------------------
from CustomTypes import CustomType								# 如果要导出一个自定义类型，则该类型必须继承于 CustomValue，并实现 __repr__ 方法
from CustomTypes import StringTemplate							# 可以识别为字符串模板的导出类

# --------------------------------------------------------------------
# explainer
# --------------------------------------------------------------------
# 元素值解释器
from explainers.ex_base import ex_base							# 表格内容解释器基类
from explainers.ex_base import ex_col_base						# 对表格中指定列进行解释的解释器基类，继承于 ex_base
from explainers.ex_base import ex_orign_col						# 对表格中指定列原值返回的解释器，继承于 ex_col_base

from explainers.ex_value_col import ex_value_col_base			# 对表格中指定列解释为指定类型值的解释器，继承于 ex_col_base
from explainers.ex_value_col import ex_str_col					# 对表格中指定列解释为一个字符串的解释器，继承于 ex_value_col_base（与 ex_orign_col 的区别是，它支持默认值，如果表格为空，则返回默认值）
from explainers.ex_value_col import ex_stpl_col					# 对表格中指定列解释为一个字符串模板的解释器，继承于 ex_str_col
from explainers.ex_value_col import ex_bool_col					# 对表格中指定列解释为一个布尔值的解释器，继承于 ex_value_col_base
from explainers.ex_value_col import ex_int_col					# 对表格中指定列解释为一个整型值的解释器，继承于 ex_value_col_base
from explainers.ex_value_col import ex_enum_col					# 对表格中指定列解释为一个整型（这些整型从指定的列表中选取）值的解释器，继承于 ex_int_col
from explainers.ex_value_col import ex_hlint_col				# 对表格中指定列解释为一个十六进制整形的解释器，继承于 ex_value_col_base
from explainers.ex_value_col import ex_float_col				# 对表格中指定列解释为一个浮点数的解释器，继承于 ex_value_col_base
from explainers.ex_value_col import ex_xfloat_col				# 对表格中指定列解释为一个可指定小数点位数的浮点数的解释器，继承于 ex_value_col_base
from explainers.ex_value_col import ex_scale_col				# 对表格中指定列解释为一个默认值为 1.0 的解释器，继承于 ex_float_col

from explainers.ex_array_col import ex_array_col_base			# 对表格中指定列解释为一个元组的解释器基类，继承于 ex_col_base
from explainers.ex_array_col import ex_onetype_array_col		# 对表格中指定列解释为一个给定元素类型的元组（所有元素同一类型）解释器，继承于 ex_array_col_base
from explainers.ex_array_col import ex_str_array_col			# 对表格中指定列解释为一个字符串类型元素元组的解释器，继承于 ex_onetype_array_col
from explainers.ex_array_col import ex_stpl_array_col			# 对表格中指定列解释为一个字符串模板类型元素元组的解释器，继承于 ex_str_array_col
from explainers.ex_array_col import ex_bool_array_col			# 对表格中指定列解释为一个布尔类型元素元组的解释器，继承于 ex_onetype_array_col
from explainers.ex_array_col import ex_int_array_col			# 对表格中指定列解释为一个整型类型元素元组的解释器，继承于 ex_onetype_array_col
from explainers.ex_array_col import ex_enum_array_col			# 对表格中指定列解释为一个整型类型元素（这些整型从指定的列表中选取）元组的解释器，继承于 ex_int_array_col
from explainers.ex_array_col import ex_henum_array_col			# 对表格中指定列解释为一个十六进制整型类型元素（这些整型从指定的列表中选取）元组的解释器，继承于 ex_hlint_array_col
from explainers.ex_array_col import ex_hlint_array_col			# 对表格中指定列解释为一个十六进制整型类型元素元组的解释器，继承于 ex_onetype_array_col
from explainers.ex_array_col import ex_float_array_col			# 对表格中指定列解释为一个浮点型元素元组的解释器，继承于 ex_onetype_array_col
from explainers.ex_array_col import ex_xfloat_array_col			# 对表格中指定列解释为一个可指定小数点后位数的浮点型元素元组的解释器，继承于 ex_onetype_array_col
from explainers.ex_array_col import ex_multitype_array_col		# 对表格中指定列解释为一个给定多个元素类型的元组（各元素类型可能不同）解释器，继承于 ex_array_col_base

from explainers.ex_inlay_array_col import ex_list_tuple_col		# 将表格中一列中的内容，解释为一个元组列表（二维数组）

from explainers.ex_inlay_exp_array import ex_inlay_exp_list		# 将多个解释器的解释结果组成一个列表返回，如果某个解释器返回 ABANDON_COL，则不将其解释结果放入到返回的列表中
from explainers.ex_inlay_exp_array import ex_inlay_exp_tuple	# 将多个解释器的解释结果组成一个元组返回，如果某个解释器返回 ABANDON_COL，则不将其解释结果放入到返回的元组中
from explainers.ex_inlay_exp_array import ex_inlay_exp_set		# 将多个解释器的解释结果组成一个集合返回，如果某个解释器返回 ABANDON_COL，则不将其解释结果放入到返回的元组中
from explainers.ex_inlay_exp_array import ex_inlay_exp_frozenset	# 将多个解释器的解释结果组成一个冻结集合返回，如果某个解释器返回 ABANDON_COL，则不将其解释结果放入到返回的元组中

from explainers.ex_key import ex_key_col						# 对表格中指定列解释为指定类型值，并将该值作为导出字典主键的解释器，继承于 ex_col_base
from explainers.ex_key import ex_key_cols						# 对表格中指定多个列合并为一个元组，然后将该元组作为导出字典主键的解释器，继承于 ex_base
from explainers.ex_key import ex_key_str_col					# 对表格中指定列解释为一个字符串，并将该字符串作为导出字典主键的解释器，继承于 ex_key_col
from explainers.ex_key import ex_key_int_col					# 对表格中指定列解释为一个整型值，并将该值作为导出字典主键的解释器，继承于 ex_key_col
from explainers.ex_key import ex_key_hlint_col					# 对表格中指定列解释为一个十六进制整型值，并将该值作为导出字典主键的解释器，继承于 ex_key_col
from explainers.ex_key import ex_key_tuple_col					# 对表格中指定列解释为一个元组（各元素类型不一定相同），并将该元组作为导出字典主键的解释器，继承于 ex_array_col_base
from explainers.ex_key import ex_key_row						# 以表格中的行号（作一个偏移）作为导出字典主键的解释器，继承于 ex_base

# 异常类
from explainers.ExplainExceptions import ExplainException					# 参数：1、message
from explainers.ExplainExceptions import ExplainFixException				# 参数：1、语言文件中 <explain> 下的某个子节点；2、格式化参数
from explainers.ExplainExceptions import ExplainErrorValueTypeException		# 数据源中数据类型异常。参数：1、数据源；2、所在行；3、列名

# --------------------------------------------------------------------
# data source table
# --------------------------------------------------------------------
from data_srcs.DataSource import iDataSource						# 数据源基类，包含一个表格成员
from data_srcs.excel import tb_csv									# csv 表格
from data_srcs.excel import tb_xlsx									# excel 标准表格


# --------------------------------------------------------------------
# exporter
# --------------------------------------------------------------------
from exporter.OutInfo import ExpInfo								# 表达式信息，对应一个导出表达式，对应一个或多个 SrcDataInfo
from exporter.pydict.PyDictOutInfo import PyDictOutItemInfo			# 导出选项，每个选项对应一个导出的数据字典，对应一个或多个导出表达式
from exporter.pydict.PyDictOutInfo import PyDictOutInfo				# 导出信息类，每个导出信息类对象对应一个导出配置

# --------------------------------------------------------------------
# engine
# --------------------------------------------------------------------
import engine														# engine 只有一个函数：exit(exitCode) 立刻退出程序，如果希望提示导出失败，则传入 exitCode = 0


# --------------------------------------------------------------------
# 界面
# --------------------------------------------------------------------
import theme
from theme import *
from theme import Printer
from theme.Printer import *
