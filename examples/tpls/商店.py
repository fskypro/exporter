# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
csv1 = tb_xlsx.getDataSource({
	"1": r"1-开发环境\商店\商店.xlsx",
	"2": r"2-正式环境\商店\商店.xlsx"
}[sys.argv[2]], "商品", 0, 1)

out = {
	"1": r"1-开发环境\商店\store.conf",
	"2": r"2-正式环境\商店\store.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 邮件配置
# ---------------------------------------------------------------------------------------
exp1 = { ex_key_str_col("商品类别"): {
	"storeID": ex_int_col("商品编号"),
	"item": {
		"id": ex_int_col("对应的物品编号"),
		"amount": ex_int_col("商品数量"),
		"freeAmount": ex_int_col("赠送数量"),
		"payType": ex_int_col("支付类别", fixValues = (1, 2)),			# 只允许填写 1 或 2
		"price": ex_int_col("价格"),
		"dsp": ex_orign_col("商品描述"),
		"ostypes": ex_int_array_col("客户端系统类别"),
		"hot": ex_int_col("是否是热销商品")}
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
		typeItem = datas.get(key, OrderDict())				# 商品类别
		datas[key] = typeItem
		if (value["item"]["payType"] == 1):					# 如果是货币支付，则将 “元” 单位转化为 “分” 单位，即乘以 100
			value["item"]["price"] *= 100
		typeItem[value["storeID"]] = value["item"]
		return KEYRET_NORMAL

# 导出信息
outInfo = TarsOutInfo(
	out,
	OutItemInfo1("Main", ExpInfo(exp1, csv1)),
	isWriteHeader = True,
	comment ="商店商品配置",
	servers = ["dbserver", "gameserver"])
