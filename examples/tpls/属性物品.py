# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
paths = {
	"1": r"1-开发环境\属性物品\属性物品.xlsx",
	"2": r"2-正式环境\属性物品\属性物品.xlsx",
}
csv1 = tb_xlsx.getDataSource(paths[sys.argv[2]], "属性", 1, 2)
csv2 = tb_xlsx.getDataSource(paths[sys.argv[2]], "礼品", 1, 2)
csv3 = tb_xlsx.getDataSource(paths[sys.argv[2]], "物品列表", 1, 2)

# 导出
out = {
	"1": r"1-开发环境\属性物品\propitems.conf",
	"2": r"2-正式环境\属性物品\propitems.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 物品配置
# ---------------------------------------------------------------------------------------
# 属性表
exp1 = { ex_key_str_col("属性编号"): OrderDict([
	("type", 1),
	("id", ex_int_col("属性编号", fixValues=xrange(1, 1000))),
	("name", ex_orign_col("属性名称")),
	("icon", ex_orign_col("属性图标")),
	("dsp", ex_orign_col("属性描述")),
	("first", ex_int_col("首次赠送数量")),
	("overlapped", 1),						# 属性一定可以叠加
	("discarded", ex_bool_col("是否废弃")),
])}

# 礼品表
exp2 = { ex_key_str_col("礼品编号"): OrderDict([
	("type", 2),
	("id", ex_int_col("礼品编号", fixValues=xrange(1001, 10000))),
	("name", ex_orign_col("礼品名称")),
	("icon", ex_orign_col("礼品图标")),
	("dsp", ex_orign_col("礼品描述")),
	("first", ex_int_col("首次赠送数量")),
	("overlapped", 1),									# 礼品一定可以叠加
	("discarded", ex_bool_col("是否废弃")),
	("giveToMail", ex_int_col("是否赠送到邮箱", 1)),

	("giveCost", ex_int_col("赠送价格")),
	("clearCost", ex_int_col("清除价格")),
	("sellCost", ex_int_col("变卖价格")),
])}

# 普通物品表
exp3 = { ex_key_str_col("物品编号", fntRet=lambda x: "item" + str(x)) : OrderDict([
	("type", 3),
	("id", ex_int_col("物品编号", fixValues=xrange(10001, 99999999))),
	("name", ex_str_col("物品名称")),
	("icon", ex_orign_col("物品图标", fnRet=lambda x: ABANDON_COL if x == "" else x)),	# 如果不填，则不导出
	("dsp", ex_orign_col("物品描述")),
	("first", ex_int_col("首次赠送数量")),
	("discarded", ex_bool_col("是否废弃")),

	("itype", ex_int_col("物品类别", fixValues=xrange(7))),
	("overlapped", ex_int_col("是否可叠加", 1)),
	("model", ex_orign_col("物品模型", fnRet=lambda x: ABANDON_COL if x == "" else x)),	# 如果不填，则不导出
	("wearSite", ex_int_col("穿戴部位", fixValues=xrange(1, 11))),
	("validTime", ex_int_col("有效时间")),
	("currencyValue", ex_int_col("货币价值")),
	("kitbagOrder", ex_int_col("摆放优先级")),
	("useType", ex_int_col("使用类别")),
	("useParam", ex_orign_col("使用参数")),
])}

class OutItemInfo(TarsOutItemInfo):
	__colNames = {}
	def onRowScanning(self, datas, key, value, row, dsrc):
		if (value.pop("discarded")):
			return KEYRET_NORMAL			# 排除被废弃的行
		if value["type"] == 3:
			# 如果具有有效时间，则一定不可叠加
			if value["validTime"] > 0:
				value["overlapped"] = 0

# ---------------------------------------------------------------------------------------
# 导出信息
# ---------------------------------------------------------------------------------------
outInfo = TarsOutInfo(
	out,
	OutItemInfo("Main", ExpInfo(exp1, csv1), ExpInfo(exp2, csv2), ExpInfo(exp3, csv3)),	# 三表合并导出
	isWriteHeader = True,
	comment ="物品配置",
	servers = ["dbserver", "gameserver", "mailserver", "lotteryserver"])
