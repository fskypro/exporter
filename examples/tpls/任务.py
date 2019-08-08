# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from exporter.ExportExceptions import ExportException
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo		# 在 exporter\TableExporter\plugins\tars 中
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
xlsxs = {
	"1": r"1-开发环境\任务\任务.xlsx",
	"2": r"2-正式环境\任务\任务.xlsx"
}
xlsx1 = tb_xlsx.getDataSource(xlsxs[sys.argv[2]], "签到任务", 0, 1)
xlsx2 = tb_xlsx.getDataSource(xlsxs[sys.argv[2]], "普通任务", 1, 2)

# 导出配置
out = {
	"1": r"1-开发环境\任务\quest.conf",
	"2": r"2-正式环境\任务\quest.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 导出表达式
# ---------------------------------------------------------------------------------------
# 签到任务
exp1 = { ex_key_int_col("任务编号"): OrderDict([
	("qtypeid", ex_int_col("任务类别编号", fixValues=xrange(0,4))),
	("typeName", ex_orign_col("任务类别名称")),
	("fullSignRewardIcon", ex_orign_col("满签奖励图标")),
	("fullSignRewardid", ex_int_col("满签奖励物品")),
	("fullSignRewardCount", ex_int_col("满签奖励物品数量")),

	("qitem", OrderDict([
		("name", ex_str_col("任务名称")),
		("dsp", ex_orign_col("任务描述")),

		("rewardid", ex_int_col("奖励属性或物品编号")),
		("rewardCount", ex_int_col("奖励数量")),
		("rewardIcon", ex_orign_col("奖励图标")),
	]))
])}

# 普通任务
exp2 = { ex_key_int_col("任务编号"): {
	"qtypeid": ex_int_col("任务类别编号"),
	"typeName": ex_orign_col("任务类别名称"),

	"qitem": OrderDict([
		("name", ex_str_col("任务名称")),
		("dsp", ex_orign_col("任务描述")),

		("ostypes", ex_int_array_col("客户端系统类型", fixValues=(0, 1, 2))),
		("opened", ex_int_col("是否开放", 1)),
		("preQuest", ex_int_array_col("前置任务", 2, [])),

		("startTime", ex_orign_col("活动起始日期")),
		("startTime", ex_orign_col("活动结束日期")),
		("monthScopes", ex_orign_col("月区间")),
		("weekScopes", ex_orign_col("周区间")),
		("dayScopes", ex_orign_col("日时区间")),

		("rewardid", ex_int_col("奖励属性或物品编号")),
		("rewardCount", ex_int_col("奖励数量")),
		("rewardIcon", ex_orign_col("奖励图标")),

		("eventid", ex_hlint_col("任务事件编号", 0, 4)),
		("eventArgs", ex_orign_col("事件参数")),
		("eventCount", ex_int_col("需要完成的事件数量", 1)),
	])
}}

# ---------------------------------------------------------------------------------------
# 导出整理
# ---------------------------------------------------------------------------------------
# 任务事件
questEvents = Enum([
	"E_QEVENT_SHARE_DALY                = 0x0001",        # 每日分享
	"E_QEVENT_SHARE_BILL                    = 0x0002",       # 账单分享
	"E_QEVENT_SHARE_GOODCARDS   = 0x0003",       # 豪牌分享
	"E_QEVENT_SHARE_AWARD            = 0x0004",       # 中奖分享

	"E_QEVENT_VERSUS                           = 0x0101",       # 对局
	"E_QEVENT_ORGANIZE                      = 0x0102",       # 组局

	"E_QEVENT_SIGN                                = 0x0201",       # 签到
])

# 签到任务
class OutItemInfo1(TarsOutItemInfo):
	def __init__(self, name, *expInfos, **attrs):
		TarsOutItemInfo.__init__(self, name, *expInfos, **attrs)
		self.__qtypeid = 0

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
		qtypeid = value.pop("qtypeid")
		if self.__qtypeid == 0:
			if qtypeid == 0:
				raise ExportException("必须在首行(第 %d 行)指定签到任务的类别编号" % (row + 1))
			self.__qtypeid = qtypeid
		if self.__qtypeid not in datas:
			datas[self.__qtypeid] = OrderDict()
			datas[self.__qtypeid] = value

		# 签到为固定的事件编号
		qitem = value.pop("qitem")
		datas[self.__qtypeid][key] = qitem
		qitem["eventid"] = hlint(questEvents.E_QEVENT_SIGN, 4)
		qitem["eventArgs"] = ""
		qitem["eventCount"] = 1
		return KEYRET_NORMAL

# 普通任务
class OutItemInfo2(TarsOutItemInfo):
	def __init__(self, name, *expInfos, **attrs):
		TarsOutItemInfo.__init__(self, name, *expInfos, **attrs)
		self.__qtypeid = 0

	def onRowScanning(self, datas, key, value, row, dsrc):
		qtypeid = value.pop("qtypeid")
		if (self.__qtypeid == 0):
			if qtypeid == 0:
				raise ExportException("必须在首行(第 %d 行)指定普通任务的类别编号" % (row + 1))
		elif qtypeid > 30000:
			raise ExportException("普通任务类别编号必须小于 30000")
		if qtypeid  > 0 and qtypeid not in datas:
			self.__qtypeid = qtypeid
			datas[self.__qtypeid] = value
		qitem = value.pop("qitem")
		datas[self.__qtypeid][key] = qitem

		# 前置任务校验
		if len(qitem["preQuest"]) > 0:
			qtypeid, qid = qitem["preQuest"]
			if qtypeid not in datas:
				raise ExportException("第 %d 行指定的前置任务类别不存在" % (row + 1))
			if qid not in datas[qtypeid]:
				raise ExportException("第 %d 行指定的前置任务编号不存在" % (row + 1))

		if not questEvents.hasEnumValue(qitem["eventid"]):
			raise ExportException("第 %d 行指定的 \”任务事件编号\“ 不存在" % (row + 1))
		return KEYRET_NORMAL

	def onAllScanned(self, datas):
		datas.update(outInfo1.outItemInfos[0].datas)

	@property
	def srcTexts(self):
		return [xlsx1.getSrcText(), xlsx2.getSrcText()]

# ---------------------------------------------------------------------------------------
# 导出信息
# ---------------------------------------------------------------------------------------
outInfo1 = TarsOutInfo(
	None,													# 不导出文件
	OutItemInfo1("Main", ExpInfo(exp1, xlsx1)))			# 导出选项信息

outInfo2 = TarsOutInfo(out,
	OutItemInfo2("Main", ExpInfo(exp2, xlsx2)),
	isWriteHeader = True,
	comment ="任务配置",
	servers = "questserver")

outInfos = [outInfo1, outInfo2]
