# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo		# 在 exporter\TableExporter\plugins\tars 中
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
csv1 = tb_xlsx.getDataSource({
	"1": r"1-开发环境\邮箱\邮箱.xlsx",
	"2": r"2-正式环境\邮箱\邮箱.xlsx",
}[sys.argv[2]], "邮箱配置", 0, 1)

csv2 = tb_xlsx.getDataSource({
	"1": r"1-开发环境\邮箱\邮箱.xlsx",
	"2": r"2-正式环境\邮箱\邮箱.xlsx",
}[sys.argv[2]], "邮件模板列表", 1, 2)

# 导出文件
out1 = {
	"1": r"1-开发环境\邮箱\mailserver.conf",
	"2": r"2-正式环境\邮箱\mailserver.conf",
}[sys.argv[2]]

out2 = {
	"1": r"1-开发环境\邮箱\mail_templates.conf",
	"2": r"2-正式环境\邮箱\mail_templates.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 邮件配置
# ---------------------------------------------------------------------------------------
exp1 = { ex_key_int_col("邮件内容编号"): {
	"keepDays": ex_int_col("邮件保存天数"),
	"keepCount": ex_int_col("邮件保存总数"),
	"mailIcons": ex_str_col("邮件图标")
	}}

class OutItemInfo1(TarsOutItemInfo):
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
		if value["keepDays"] > 0:
			datas["keepDays"] = value["keepDays"]
		if value["keepCount"] > 0:
			datas["keepCount"] = value["keepCount"]
		if value["mailIcons"] != "":
			icons = datas.get("mailIcons", {})
			icons[key] = value["mailIcons"]
		datas["mailIcons"] = icons
		return KEYRET_NORMAL

# ---------------------------------------------------------------------------------------
# 邮件模板列表
# ---------------------------------------------------------------------------------------
# 导出表达式
exp2 = {ex_key_int_col("邮件编号"): {
	"mailType": ex_int_col("邮件类别编号", fixValues=xrange(1, 3)),	# xrange(1, 3) 表示限制填写 1 ~ 3 之间的值，否则导出时报错
	"title": ex_orign_col("邮件标题"),
	"content": ex_orign_col("邮件内容"),
	"contentType": ex_int_col("内容编号", 1),							# 第二个参数表示默认值（即，如果 excel 格子中不填写内容，则使用该值）
	"sender": ex_orign_col("发送者名称"),
	"stuffs": ex_inlay_exp_tuple(
		ex_int_array_col("附件1", 2, None),
		ex_int_array_col("附件2", 2, None),
		ex_int_array_col("附件3", 2, None),
		ex_int_array_col("附件4", 2, None),
		ex_int_array_col("附件5", 2, None)),
	}}

class OutItemInfo2(TarsOutItemInfo):
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
		dstuff = {}
		stuffs = value.pop("stuffs")
		index = 1
		for stuff in stuffs:
			if stuff is None: continue
			else: dstuff[stuff[0]] = stuff[1]
			index += 1
		value["stuffs"] = dstuff

		if not value.has_key("type"): return None
		return None

# 导出信息
outInfo1 = TarsOutInfo(
	out1,														# 导出文件
	OutItemInfo1("Main", ExpInfo(exp1, csv1)),				# 导出选项信息
	isWriteHeader = True,
	comment ="邮箱配置",
	servers = "mailserver")

outInfo2 = TarsOutInfo(
	out2,
	OutItemInfo2("Main", ExpInfo(exp2, csv2)),
	isWriteHeader = True,
	comment ="邮件模板",
	servers = "mailserver")

outInfos = [outInfo1, outInfo2]