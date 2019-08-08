# -*- coding: utf-8 -*-
#

import os
from TableExporter import *
from json.JsonOutInfo import JsonOutInfo

# -----------------------------------------------------------------------------
# 加密器
# -----------------------------------------------------------------------------
class ENC(object):
	def __init__(self):
		cfg = Path.realToExecutePath("../../../src/datas/server/config.json")
		try:
			file = open(cfg, "r")
			stream = file.read()
			dct = eval(stream)
			self.__packkey = dct["cfgEncrypt"]["unpackkey"]					# 密匙
			self.__discretValue = dct["cfgEncrypt"]["discretValue"]			# 加密离散键，等于双密匙
		except:
			messageBox("无法打开配置文件：%s，或配置格式不正确，导出失败！" % cfg, "错误", MB_OK)
			engine.exit(1)
		finally:
			file.close()

		self.__index = -1

	# -----------------------------------------------------------------
	# private
	# -----------------------------------------------------------------
	def __calcRuleList(self):
		ruleItems = []
		for i in xrange(3, self.__discretValue + 3):
			ruleItems.append((self.__packkey % i) + 1)
		return ruleItems

	def __packByte(self, byte):
		if self.__index % 4 == 0:
			return 0xff ^ (256 - ord(byte))
		elif self.__index % 4 == 1:
			return 256 - (0xff ^ ord(byte))
		elif self.__index % 4 == 2:
			return 256 - ord(byte)
		return 0xff ^ ord(byte)

	def __getCount(self, count, rules):
		if count <= 0:
			self.__index = (self.__index + 1) % len(rules)
			return rules[self.__index]
		return count - 1


	# -----------------------------------------------------------------
	# public
	# -----------------------------------------------------------------
	def pack(self, srcStream, dstStream):
		"""
		加密文件流
		"""
		self.__index = -1
		rules = self.__calcRuleList()
		count = 0
		while True:
			byte = srcStream.read(1)
			if byte == "": break;
			count = self.__getCount(count, rules)
			byte = chr(self.__packByte(byte))
			dstStream.write(byte)

	def packString(self, text, dstStream):
		"""
		加密字符串
		"""
		self.__index = -1
		rules = self.__calcRuleList()
		count = 0
		for ch in text:
			count = self.__getCount(count, rules)
			byte = chr(self.__packByte(ch))
			dstStream.write(byte)

	def unpack(self, filePath):
		"""
		解密
		"""
		def unpackByte(byte, index):
			if index % 4 == 0:
				return 256 - (0xff ^ ord(byte))
			elif index % 4 == 1:
				return 0xff ^ (256 - ord(byte))
			elif index % 4 == 2:
				return 256 - ord(byte)
			return 0xff ^ ord(byte)

		self.__index = -1
		rules = self.__calcRuleList()
		ruleCount = len(rules)
		def getCount(count):
			if count <= 0:
				self.__index = (self.__index + 1) % ruleCount
				return rules[self.__index]
			return count - 1

		file = open(filePath, "rb")
		dstFilePath = os.path.splitext(filePath)[0] + "1.json"
		dstFile = open(dstFilePath, "wb")
		count = 0
		while True:
			byte = file.read(1)
			if byte == "": break;
			count = getCount(count)
			byte = chr(unpackByte(byte, self.__index))
			dstFile.write(byte)
		dstFile.close()



# -----------------------------------------------------------------------------
# 导出时统一加密
# -----------------------------------------------------------------------------
class ConfigOutInfo(JsonOutInfo):
	def __init__(self, *args, **dargs):
		JsonOutInfo.__init__(self, *args, **dargs)
		#self.__enc = ENC()

	def onWriteClosed(self):
		return
		srcFilePath = self.dstFile
		srcFile = open(srcFilePath, "rb")

		dstFilePath = Path.changeExtention(srcFilePath, ".data")
		try:
			dstFile = open(dstFilePath, "wb")
		except:
			messageBox("写入客户端配置失败，请查看文件是否被占用：%s" % dstFilePath, "错误", MB_OK)
			engine.exit(1)

		self.__enc.pack(srcFile, dstFile)
		srcFile.close()
		dstFile.close()

		# 解密测试
		#self.__enc.unpack(dstFilePath)
