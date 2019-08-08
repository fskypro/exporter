# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo		# 在 exporter\TableExporter\plugins\tars 中
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# ---------------------------------------------------------------------------------------
# 数据源
# ---------------------------------------------------------------------------------------
# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
xlsx = tb_xlsx.getDataSource({
	"1": r"1-开发环境\分红权\分红权.xlsx",
	"2": r"2-正式环境\分红权\分红权.xlsx",
}[sys.argv[2]], "能量值兑换表", 0, 1)

out = {
	"1": r"1-开发环境\分红权\point2bonus.conf",
	"2": r"2-正式环境\分红权\point2bonus.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 导出表达式
# ---------------------------------------------------------------------------------------
exp = { ex_key_row(): {
	"name": ex_str_col("名称"),
	"points": ex_int_col("积分"),
	"bonuses": ex_int_col("股权数")
	}}


# ---------------------------------------------------------------------------------------
# 导出信息
# ---------------------------------------------------------------------------------------
outInfo = TarsOutInfo(
	out,
	TarsOutItemInfo("Main", ExpInfo(exp, xlsx)),
	comment ="能量值与股权兑换映射表",
	servers = "bonusserver")
