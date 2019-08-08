# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from exporter.ExportExceptions import ExportException
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
csvFiles = {
	"1": r"1-开发环境\\金币场撮合\\金币场撮合.xlsx",
	"2": r"2-正式环境\\金币场撮合\\金币场撮合.xlsx",
}
csv = tb_xlsx.getDataSource(csvFiles[sys.argv[2]], "金币场撮合", 1, 2)

# 输出文件
outFile = {
	"1": "1-开发环境\\金币场撮合\\casinos.conf",
	"2": "2-正式环境\\金币场撮合\\casinos.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 邮件配置
# ---------------------------------------------------------------------------------------
exp = { ex_key_int_col("玩法编号"): {
	"name": ex_orign_col("玩法名称"),
	"icon": ex_orign_col("玩法图标"),
	"opened": ex_int_col("玩法是否开放", 1),
	"serverObj": ex_orign_col("运行的服务器对象"),
	"ostypes": ex_int_array_col("玩法客户端系统", fixValues=xrange(0, 3)),
	"isHot": ex_int_col("是否是热门玩法"),
	"casino": OrderDict([
		("id", ex_int_col("场次编号")),
		("name", ex_str_col("场次名称")),
		("icon", ex_orign_col("场次图标")),
		("opened", ex_int_col("场次是否开放", 1)),
		("ostypes", ex_int_array_col("场次客户端系统", fixValues=xrange(0, 3))),
		("basePoint" , ex_int_col("积分奖励基数")),
		("maxFan", ex_int_col("封顶倍数")),
		("isHot", ex_int_col("是否是热门场次")),
		("isSwap3", ex_int_col("是否换三张")),

		("baseScore", ex_int_array_col("底分")),
		("minChips", ex_int_col("最小准入金币数")),
		("maxChips", ex_int_col("最大准入金币数")),
		("rentCost", ex_int_col("台费")),
		("minNextCoins", ex_int_col("下一场最低分")),

		("tmin", ex_float_col("最小撮合时间")),
		("tmax", ex_float_col("最大撮合时间")),
		("minMatchCount", ex_int_col("最小起撮人数")),
		("minMatchBase", ex_int_col("最小起撮人数低值")),
		("minMatchTop", ex_int_col("最小起撮人数峰值")),
		("minMatchInc", ex_int_col("最小起撮人数增减值")),
		("ai", ex_list_tuple_col("AI级别和几率", (int, float))),

		("aiTactics", ex_int_col("AI策略")),
		("userTactics" , ex_int_col("用户策略")),
		("warmTactics",  ex_int_col("温暖局策略")),
		("warmValue", ex_int_col("温暖额度")),
		("warmMinTime", ex_float_col("温暖局最小进入时间")),
		("warmMaxTime", ex_float_col("温暖局最大进入时间")),
		])
	}}

class OutItemInfo(TarsOutItemInfo):
	def onRowScanning(self, datas, key, value, row, dsrc):
		"""
		每解释一行时被调用，还没添加进 datas
		@param			datas: 整个数据表
		@param			key  : 当前解释到的行的 key
		@param			value: 当前行数据值
		@param			row  : 当前解释到的行索引
		@param			dsrc : 当前行所在数据源信息
		@return			         : None/KEYRET_NORMAL/KEYRET_EMPTY/KEYRET_IGNOR
						       None 正常导出
						       KEYRET_NORMAL 不导出并且不提示
						       KEYRET_EMPTY 认为空行提示
						       KEYRET_IGNOR 认为该行忽略并提示
		"""
		if key not in datas:
			datas[key] = value
		sample = datas[key]
		casino = value.pop("casino")
		casinoID = casino.pop("id")
		sample[casinoID] = casino

		odds = 0
		ai = OrderDict()
		aiInfos = casino["ai"]
		for lv, odd in aiInfos:
			ai[lv] = odd
			odds += odd
		casino["ai"] = ai
		if odds != 100:
			raise ExportException("第 %i 行的 ai 几率总值合计没有等于 100" % (row + 1))
		return KEYRET_NORMAL

# 导出信息
outInfo = TarsOutInfo(
		outFile,
		OutItemInfo("Main", ExpInfo(exp, csv)),
		isWriteHeader = True,
		comment ="金币场撮合配置",
		servers = ["casinoserver", "gameserver"])
