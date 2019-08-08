# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from exporter.ExportExceptions import ExportException
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo		# 在 exporter\TableExporter\plugins\tars 中
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
xlsxs = ({
	1: r"1-开发环境\抽奖\抽奖.xlsx",
	2: r"2-正式环境\抽奖\抽奖.xlsx",
})

arg = int(sys.argv[2])
xlsx0 = tb_xlsx.getDataSource(xlsxs[arg], "全局参数设置", 0, 1)
xlsx1 = tb_xlsx.getDataSource(xlsxs[arg], "中奖物品", 0, 1)
xlsx2 = tb_xlsx.getDataSource(xlsxs[arg], "抽奖类别", 0, 1)
xlsx3 = tb_xlsx.getDataSource(xlsxs[arg], "单独抽奖", 0, 1)
xlsx4 = tb_xlsx.getDataSource(xlsxs[arg], "大盘池", 0, 1)

# 导出文件
out = {
	1: "1-开发环境\抽奖\lottery.conf",			# 开发配置
	2: "2-正式环境\抽奖\lottery.conf",			# 正式配置
}[arg]

# ---------------------------------------------------------------------------------------
# 导出表达式
# ---------------------------------------------------------------------------------------
# 全局参数设置
exp0 = { ex_key_int_col("ID"): {
	"deductRate": ex_float_col("投入大奖池比例"),
	"deductPower": ex_float_col("大盘池开奖扣除倍数")
}}

# 中奖物品
exp1 = { ex_key_int_col("奖品编号"): OrderDict([
	("propItemID", ex_int_col("对应物品编号")),
	("amount", ex_int_col("物品数量")),
	("icon", ex_orign_col("奖品图标"))
	])}

# 抽奖类别
exp2 = { ex_key_int_col("类别编号") : {
	"cost": ex_int_col("花费钻石数"),
	"count": ex_int_col("抽奖次数")
}}

# 单独抽奖
exp3 = { ex_key_int_col("抽奖编号"): OrderDict([
	("rewardid", ex_int_col("奖品编号")),
	("odds", OrderDict([
		(0, ex_float_col("默认系统中奖几率")),
		(1, ex_float_col("安卓机器中奖几率")),
		(2, ex_float_col("IOS机器中奖几率"))
	]))
])}

# 大盘池
exp4 = { ex_key_int_col("级别编号") : OrderDict([
	("diamons", ex_int_col("开奖钻石数")),
	("rewards", [
		ex_multitype_array_col("奖励物品1", (int, float), None),
		ex_multitype_array_col("奖励物品2", (int, float), None),
		ex_multitype_array_col("奖励物品3", (int, float), None),
		ex_multitype_array_col("奖励物品4", (int, float), None),
		ex_multitype_array_col("奖励物品5", (int, float), None),
		ex_multitype_array_col("奖励物品6", (int, float), None),
	])
])}

# ---------------------------------------------------------------------------------------
# 重载大盘池导出选项
# ---------------------------------------------------------------------------------------
class OutItemInfo3(TarsOutItemInfo):
	def onRowScanning(self, datas, key, value, row, dsrc):
		"""
		每解释一行时被调用，还没添加进 datas
		@param			datas: 整个数据表
		@param			key  : 当前解释到的行的 key
		@param			value: 当前行数据值
		@param			row  : 当前解释到的行索引
		@param			dsrc : 当前行所在数据源信息
		@return			     : None/KEYRET_NORMAL/KEYRET_EMPTY/KEYRET_IGNOR
						       None 正常导出
						       KEYRET_NORMAL 不导出并且不提示
						       KEYRET_EMPTY 认为空行提示
						       KEYRET_IGNOR 认为该行忽略并提示
		"""
		if value["rewardid"] not in outInfo1.outItemInfos[0].datas:
			raise ExportException("数据源:%s 中，第 %i 行，“奖励编号” 列指定的奖励编号不存在！" % (dsrc.fileName, row+1))

class OutItemInfo4(TarsOutItemInfo):
	def onRowScanning(self, datas, key, value, row, dsrc):
		rewardTable = outInfo1.outItemInfos[0].datas

		rewards = {}
		count = 1
		for reward in value["rewards"]:
			if reward is None: continue
			if (reward[0] not in rewardTable):
				raise ExportException("数据源:%s 中，第 %i 行，“奖励物品%i” 列指定的奖励编号不存在！" % (dsrc.fileName, row+1, count))
			rewards[reward[0]] = reward[1]
			count += 1
		value["rewards"] = rewards

	def onAllScanned(self, datas):
		"""
		全部扫描完毕后被调用
		"""
		datas0 = outInfo0.outItemInfos[0].datas
		datas1 = outInfo1.outItemInfos[0].datas
		datas2 = outInfo2.outItemInfos[0].datas
		datas3 = outInfo3.outItemInfos[0].datas
		datas4 = datas.clone()
		datas.clear()
		datas["rewardItems"] = datas1
		datas["ltypes"] = datas2
		datas["single"] = datas3
		datas["global"] = datas4

		datas3.topinsert(("deductRate", datas0[1]["deductRate"]))
		datas4.topinsert(("deductPower", datas0[1]["deductPower"]))

	@property
	def srcTexts(self):
		return [xlsx1.getSrcText(), xlsx2.getSrcText(), xlsx3.getSrcText(), xlsx4.getSrcText()]

# ---------------------------------------------------------------------------------------
# 导出信息
# ---------------------------------------------------------------------------------------
# 全局参数设置
outInfo0 = TarsOutInfo(
	None,
	TarsOutItemInfo("Main", ExpInfo(exp0, xlsx0))
	)

# 奖品
outInfo1 = TarsOutInfo(
	None,														# 不单奖励物品单独写出文件
	TarsOutItemInfo("rewardItems", ExpInfo(exp1, xlsx1))
	)

# 抽奖类别
outInfo2 = TarsOutInfo(
	None,
	TarsOutItemInfo("ltypes", ExpInfo(exp2, xlsx2))
	)

# 单独抽奖
outInfo3 = TarsOutInfo(
	None,
	OutItemInfo3("single", ExpInfo(exp3, xlsx3))
	)

# 大盘池
outInfo4 = TarsOutInfo(
	out,
	OutItemInfo4("Main", ExpInfo(exp4, xlsx4)),
	commentKey = "__comment__",
	comment ="抽奖系统配置",
	servers = "lotteryserver")

outInfos = [outInfo0, outInfo1, outInfo2, outInfo3, outInfo4]
