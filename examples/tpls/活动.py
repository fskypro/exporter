# -*- coding: utf-8 -*-
#

import re
import sys
from TableExporter import *
from exporter.ExportExceptions import ExportException
from json.JsonOutInfo import JsonOutInfo, JsonOutItemInfo
from ConfigOutInfo import ConfigOutInfo

paths = {
	"1": r"1-开发环境\活动\活动.xlsx",
	"2": r"2-正式环境\活动\活动.xlsx",
}

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
# 新手礼包
xlsx1 = tb_xlsx.getDataSource(paths[sys.argv[2]], "新手礼包", 1, 2)
out1 = {
	"1": r"1-开发环境\活动\activity_novice.json",
	"2": r"2-正式环境\活动\activity_novice.json",
}[sys.argv[2]]

# 首充礼包
xlsx2 = tb_xlsx.getDataSource(paths[sys.argv[2]], "首充奖励", 1, 2)
out2 = {
	"1": r"1-开发环境\活动\activity_fcr.json",
	"2": r"2-正式环境\活动\activity_fcr.json",
}[sys.argv[2]]

# 限时礼包
xlsx3 = tb_xlsx.getDataSource(paths[sys.argv[2]], "限时礼包", 1, 2)
out3 = {
	"1": r"1-开发环境\活动\activity_llogin.json",
	"2": r"2-正式环境\活动\activity_llogin.json",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 导出表达式
# ---------------------------------------------------------------------------------------
# 新手礼包
exp1 = { ex_key_row(): OrderDict([
	("channelid", ex_int_col("渠道编号")),
	("ostype", ex_int_col("客户端系统编号")),
	("activityid", 1),
	("name", ex_str_col("活动名称")),
	("dsp", ex_orign_col("活动描述")),
	("icon", ex_orign_col("活动图标")),
	("closed", ex_bool_col("是否暂停")),
	("showSite", ex_int_col("显示位置")),
	("rewards", ex_list_tuple_col("礼包物品", [int, int, str])),
	])
}

# 首冲奖励
exp2 = { ex_key_row(): OrderDict([
	("channelid", ex_int_col("渠道编号")),
	("ostype", ex_int_col("客户端系统编号")),
	("activityid", 2),
	("name", ex_str_col("活动名称")),
	("dsp", ex_orign_col("活动描述")),
	("notice", ex_orign_col("活动公告")),
	("icon", ex_orign_col("活动图标")),
	("closed", ex_bool_col("是否暂停")),
	("showSite", ex_int_col("显示位置")),
	("startTime", ex_orign_col("起始时间")),
	("endTime", ex_orign_col("结束时间")),
	("minCharge", ex_int_col("最小首充值")),
	("rewards", ex_list_tuple_col("奖励物品", [int, int, str])),
	])
}

# 限时礼包
timePtn = re.compile("^(\d{1,2}):(\d{1,2}):(\d{1,2})$")
def tranTime(strTime):
	if strTime == "": return 0
	match = timePtn.match(strTime)
	if match is None: return None
	h, m, s = map(lambda x : int(x), match.groups())
	return h * 3600 + m * 60 + s

exp3 = { ex_key_row(): OrderDict([
	("channelid", ex_int_col("渠道编号")),
	("ostype", ex_int_col("客户端系统编号")),
	("activityid", 3),
	("name", ex_str_col("活动名称")),
	("dsp", ex_orign_col("活动描述")),
	("icon", ex_orign_col("活动图标")),
	("closed", ex_bool_col("是否暂停")),
	("showSite", ex_int_col("显示位置")),
	("validTimes", ex_inlay_exp_list(
		ex_inlay_exp_list(ex_str_col("起始时间1", fnRet=tranTime), ex_str_col("结束时间1", fnRet=tranTime)),
		ex_inlay_exp_list(ex_orign_col("起始时间2", fnRet=tranTime), ex_orign_col("结束时间2", fnRet=tranTime)),
		)),
	("rewards", ex_list_tuple_col("礼包物品", [int, int, str])),
	])
}

# ---------------------------------------------------------------------------------------
# 导出整理
# ---------------------------------------------------------------------------------------
class OutItemInfo(JsonOutItemInfo):
	__ptn = re.compile("^(\d{1,2}):(\d{1,2}):(\d{1,2})$")
	def tranTime(strTime, row, key):
		if strTime == "": return None
		match = self.__ptn.match(strTime)
		if match is None:
			raise ExportException("第 %d 行 ”起始时间%d“ 或 ”结束时间%d“ 填写格式错误！" % ((row + 1)), key, key)
		h, m, s = map(lambda x : int(x), m.groups())
		return h * 3600 + m * 60 + s

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
		if value.pop("closed") :
			return KEYRET_NORMAL
		if value["activityid"] == 3:				# 限时登录礼包活动校验
			validTimes = value["validTimes"]
			value["validTimes"] = []
			for idx, (start, end) in enumerate(validTimes):
				if start is None:
					raise ExportException("第 %d 行 ”起始时间%d“ 填写格式错误！" % ((row + 1), idx+1))
				if end is None:
					raise ExportException("第 %d 行 ”结束时间%d“ 填写格式错误！" % ((row + 1), idx+1))
				if start != 0 or end != 0:
					if start > 86399:
						raise ExportException("第 %d 行 ”起始时间%d“ 填写的时间超出范围！" % ((row + 1), idx+1))
					if end > 86399:
						raise ExportException("第 %d 行 ”结束时间%d“ 填写的时间超出范围！" % ((row + 1), idx+1))
					if start > end: start, end = end, start
					value["validTimes"].append((start, end))
			if len(value["validTimes"]) == 0:
				raise ExportException("第 %d 行 必须指定活动有效时间！" % (row + 1))
		return None

# ---------------------------------------------------------------------------------------
# 导出信息
# ---------------------------------------------------------------------------------------
# 新手礼包
outInfo1 = JsonOutInfo(
	out1,
	OutItemInfo(ExpInfo(exp1, xlsx1), warps=2),		# wraps 表示小于第几层嵌套内，换行
	commentKey = "__comment__",
	comment ="活动配置 -- 新手礼包",
	servers = "activityserver")

# 首充奖励活动
outInfo2 = JsonOutInfo(
	out2,
	OutItemInfo(ExpInfo(exp2, xlsx2), warps=2),
	commentKey = "__comment__",
	comment ="活动配置 -- 首冲奖励",
	servers = "activityserver")

# 首充奖励活动
outInfo3 = JsonOutInfo(
	out3,
	OutItemInfo(ExpInfo(exp3, xlsx3), warps=2),
	commentKey = "__comment__",
	comment ="活动配置 -- 限时礼包",
	servers = "activityserver")

outInfos = [outInfo1, outInfo2, outInfo3]
