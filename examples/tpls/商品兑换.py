# -*- coding: utf-8 -*-
#

import sys
from TableExporter import *
from exporter.ExportExceptions import ExportException
from tars.TarsOutInfo import TarsOutInfo, TarsOutItemInfo
from tars.TarsWidget import TarsListValue
from ConfigOutInfo import ConfigOutInfo

# 数据源信息，第二个参数表示作为标头的行，第三个参数表示数据内容的起始行（注意：第一行为 0）
csv1 = tb_xlsx.getDataSource({
	"1": r"1-开发环境\商品兑换\商品兑换.xlsx",
	"2": r"2-正式环境\商品兑换\商品兑换.xlsx",
	}[sys.argv[2]], "商品", 1, 2)

out = {
	"1": r"1-开发环境\商品兑换\goodslist.conf",
	"2": r"2-正式环境\商品兑换\goodslist.conf",
}[sys.argv[2]]

# ---------------------------------------------------------------------------------------
# 邮件配置
# ---------------------------------------------------------------------------------------
exp1 = { ex_key_int_col("商品编号"): OrderDict([
	("gtype", ex_int_col("商品类别编号", -1)),
	("gtypeName", ex_orign_col("商品类别名称")),
	("name", ex_str_col("商品名称")),
	("dsp", ex_orign_col("商品描述")),
	("icon", ex_orign_col("商品图标")),
	("amount", ex_int_col("商品数量")),
	("costItem", ex_int_col("货币类别", 2)),
	("costAmount", ex_int_col("价格")),
	("isHot", ex_int_col("是否是热销商品")),
	("isInShop", ex_int_col("是否在兑换中心", 1)),
	("stopSale", ex_int_col("暂时停售")),
	])}

class OutItemInfo1(TarsOutItemInfo):
	__gtype = -1
	__gtypeName = ""
	__gids = {}
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
		if value["gtype"] > 0:
			self.__gtype = value["gtype"]
			self.__gtypeName = value["gtypeName"]
		else:
			value["gtype"] = self.__gtype
			value["gtypeName"] = self.__gtypeName
		if key in self.__gids:
			raise ExportException("第 %d 行与第 %d 行的商品编号重复！" % (row + 1, self.__gids[key]  + 1))
		self.__gids[key] = row

		if value["costAmount"] <= 0:
			raise ExportException("第 %d 行是否忘记填写价格了？" % (row + 1))

# 导出信息
outInfo = TarsOutInfo(
	out,
	OutItemInfo1("Main", ExpInfo(exp1, csv1)),
	isWriteHeader = True,
	comment ="兑换商品列表配置",
	servers = ["exchangeserver", ])
