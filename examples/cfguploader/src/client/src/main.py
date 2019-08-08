# -*- coding: utf-8 -*-
"""
输入文件名，并且上传
"""

import os
import sys
import socket
import time
import struct
from optparse import OptionParser

class SvrCode:
	OK                                                = 0     # 正常
	ERR_IDENTITY                            = 1     # 用户不存在
	ERR_UNKNOW_ACTION          = 2     # 操作不存在
	ERR_SAVE_HISTIRY                   = 3     # 无法保存历史文件
	ERR_OPEN_FILE                         = 4     # 无法打开并保存上传文件
	ERR_RCV_UPLOAD_INFO         = 5     # 接收上传信息失败
	ERR_UNPACK_UPLOAD_INFO = 6     # 错误的上传信息包
	ERR_DST_FILE_NAME                = 7     # 错误的目标文件名
	ERR_RECV_FILE                           = 8     # 接收文件失败
	ERR_SAVE_FILE                           = 9     # 无法保存上传文件
	ERR_CMD                                    = 10    # 执行刷新配置命令失败
	NO_HISTORY_FILE                     = 11    # 历史版本不存在
	ERR_HISTORY_FILE                    = 12    # 无法恢复历史版本文件

	msgs = {
		OK                                                : "正常",
		ERR_IDENTITY                            : "用户不存在，或密匙不正确",
		ERR_UNKNOW_ACTION          : "无效操作！",
		ERR_SAVE_HISTIRY                   : "无法保存历史文件",
		ERR_OPEN_FILE                          : "无法打开并保存上传文件",
		ERR_RCV_UPLOAD_INFO         : "服务器无法接收到上传信息包",
		ERR_UNPACK_UPLOAD_INFO : "服务器解释上传信息包失败",
		ERR_DST_FILE_NAME               : "配置上传到服务器，名字必须是字母、数字或下划线",
		ERR_RECV_FILE                          : "接收文件失败",
		ERR_SAVE_FILE                          : "无法保存上传文件",
		ERR_CMD                                   : "执行刷新配置命令失败",
		NO_HISTORY_FILE                    : "历史版本文件不存在",
		ERR_HISTORY_FILE                   : "无法恢复历史版本文件"
	}

def prints(msg, *args):
	msg = msg % args
	print msg.decode("utf-8")

def info(msg, *args):
	msg = msg % args
	print "[INFO] " + msg.decode("utf-8")

def error(msg, *args):
	msg = msg % args
	print "[ERROR] " + msg.decode("utf-8")

# ---------------------------------------------------------------------------------------
# ActionBase
# ---------------------------------------------------------------------------------------
class ActionBase(object):
	# 操作码|16进制MD5密码|文件保存路径|文件大小
	ACTION_FORMAT_ = "!i40s64sL"			# 操作信息头格式
	BUFF_SIZE_ = 1024

	def __init__(self, host, port, identity):
		self.__host = host
		self.__port = port
		self.__identify = identity
		self.sock_ = None

	def __del__(self):
		if self.sock_ is not None:
			self.sock_.close()

	# 创建 socket
	def createSocket_(self):
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.settimeout(10)
		try:
			info("准备链接配置服务器：%s:%d", self.__host, self.__port)
			sock.connect((self.__host, self.__port))
		except socket.timeout, err:
			error("链接配置服务器超时.")
		except socket.error, err:
			if err.message == "":
				error('无法链接到配置服务器：%s' % self.__host)
			else:
				error('链接配置服务器失败，套接字错误：%s', err.message)
		except Exception, err:
			error("无法链接到配置服务器：%s", err.message)
		else:
			self.sock_ = sock
			info("建立连接成功！")

	# 发送操作信息头
	def sendActionInfo_(self, action, fileName, fileLen=0):
		uploadInfo = struct.pack(self.ACTION_FORMAT_, action, self.__identify, fileName, fileLen)
		try:
			self.sock_.sendall(uploadInfo)
		except Exception, err:
			error('上传 “操作头信息” 失败: %s', err.message)
			return False
		info('上传“操作头信息”成功！')
		return True

	# 接收响应包
	def receiveConfirm_(self):
		try:
			ret = self.sock_.recv(struct.calcsize("!I"))
		except Exception, err:
			return err.message

		try:
			ret = struct.unpack("!I", ret)[0]
			if ret != SvrCode.OK:
				return SvrCode.msgs.get(ret, "未知错误")
		except Exception, err:
			return err.message
		return ""

# -----------------------------------------------------------------------------
# ConfigSender
# -----------------------------------------------------------------------------
class ConfigSender(ActionBase):
	def __init__(self, host, port, identity):
		ActionBase.__init__(self, host, port, identity)

	def __sendUploadInfo(self, srcFileName, dstFileName):
		try:
			stat = os.stat(srcFileName)
		except Exception, err:
			error('获取 “配置文件” 信息失败: %s', err.message)
			return False

		if not self.sendActionInfo_(1, dstFileName, stat.st_size):
			return False

		err = self.receiveConfirm_()
		if err != "":
			error("接收 “上传配置文件信息” 返回失败，%s", err)
		else:
			info("接收 “上传配置文件信息” 返回成功")
		return err == ""

	def __sendUploadFile(self, srcFileName, dstFileName):
		try:
			fp = open(srcFileName, 'rb')
		except err:
			error("无法打开配置文件：%s", srcFileName)
			return

		try:
			while 1:
				data = fp.read(self.BUFF_SIZE_)
				if not data: break
				self.sock_.sendall(data)
		except Exception, err:
			error("上传配置文件错误：%s", err.message)
			return

		info("上传配置文件成功！")
		fp.close()

		try:
			ret = self.sock_.recv(struct.calcsize("!I"))
			ret = struct.unpack("!I", ret)[0]
			if ret != SvrCode.OK:
				error("更新配置失败：%s", SvrCode.msgs.get(ret, "未知错误！"))
			else:
				info("更新配置成功！")
		except err:
			error("无法接收更新配置返回，未知更新是否成功：%s", err.message)

	def send(self, srcFileName, dstFileName):
		self.createSocket_()
		if self.sock_ is None: return
		if (self.__sendUploadInfo(srcFileName, dstFileName)):
			self.__sendUploadFile(srcFileName, dstFileName)

# ---------------------------------------------------------------------------------------
# ConfigLister
# ---------------------------------------------------------------------------------------
class ConfigLister(ActionBase):
	def __init__(self, host, port, identity):
		ActionBase.__init__(self, host, port, identity)
		self.__fileList = {}

	# 回滚历史版本
	def __revert(self, fileName):
		while 1:
			ask = "你可以输入历史文件名前面的序号来恢复历史版本（输入其他字符退出）："
			key = raw_input(ask.decode("utf-8").encode("gbk"))
			key = key.strip()
			if key == "": continue
			if key.isdigit(): key = int(key)
			else: sys.exit(0);
			break
		if key not in self.__fileList: return

		fileName = os.path.splitext(fileName)[0]
		historyFile = os.path.join(fileName, self.__fileList[key])
		historyFile = historyFile.replace("\\", "/")

		self.createSocket_()
		if self.sock_ is None: return

		# 发送操作信息头
		info("开始发送“回滚信息头”")
		if not self.sendActionInfo_(3, historyFile):
			return

		# 接收信息头确认
		err = self.receiveConfirm_()
		if err != "":
			error("接收 “恢复历史配置文件信息” 返回失败，%s", err)
		else:
			info("接收 “恢复配置文件信息” 返回成功！")
			info("目前使用的配置文件为：%s", self.__fileList[key])

	def pull(self, configFile):
		self.createSocket_()
		if self.sock_ is None: return

		# 发送操作信息头
		if not self.sendActionInfo_(2, configFile):
			return

		# 接收信息头确认
		err = self.receiveConfirm_()
		if err != "":
			error("接收 “拉取历史配置文件信息” 返回失败，%s", err)
			return
		info("接收 “拉取配置文件信息” 返回成功！")
		prints("\n历史文件如下：")

		# 接收文件列表头信息
		headSize = struct.calcsize("!I")
		headData = self.sock_.recv(headSize)
		if len(headData) < headSize:
			error("接收文件列表失败！")
			return
		try:
			listSize = struct.unpack("!I", headData)[0]
		except Exception, err:
			error("解包文件列表头失败")
			return

		# 接收文件列表
		buff = ""
		while 1:
			if listSize <= 0: break
			if listSize > self.BUFF_SIZE_:
				data = self.sock_.recv(self.BUFF_SIZE_)
			else:
				data = self.sock_.recv(listSize)
			if not data: break
			buff += data

		# 打印文件列表
		fileList = buff.split("|")
		for idx, fileName in enumerate(fileList):
			self.__fileList[idx+1] = fileName
			prints("%d、%s", idx+1, fileName)
		self.sock_.close()
		self.__revert(configFile)

# ---------------------------------------------------------------------------------------
# application antrance
# ---------------------------------------------------------------------------------------
def main(options, action):
	try:
		file = open(options.identifyfile, "rb")
	except:
		error("无法打开密匙文件：" + options.identifyfile)
		return
	else:
		identity = file.readline()
	finally:
		file.close()

	if action == 1:
		sender = ConfigSender(options.host, options.port, identity)
		sender.send(options.filename, options.dstfilename)
	elif action == 2:
		cfgLister = ConfigLister(options.host, options.port, identity)
		cfgLister.pull(options.filename)

if __name__ == "__main__":
	parser = OptionParser()
	parser._short_opt = {"": parser._short_opt.pop("-h")}
	parser.option_list[0]._short_opts[0] = ""
	parser.add_option("-h", "--host",  action="store", dest="host", help="server address")
	parser.add_option("-p", "--port", action="store", dest="port", type=int, help="server port")
	parser.add_option("-i", "--iden", action="store", dest="identifyfile", help="identity file")
	parser.add_option("-f", "--file", action="store", dest="filename", help="upload file")
	parser.add_option("-d", "--dst", action="store", dest="dstfilename", default="", help="filename save in server")
	(options, args) = parser.parse_args()

	prints("请选择要执行的操作：")
	prints("输入 “1“ 表示上传并刷新配置")
	prints("输入 “2“ 表示显示配置上传记录")
	prints("输入其他字符退出")
	while 1:
		ask = "请输入你要执行的操作：(1/2)："
		key = raw_input(ask.decode("utf-8").encode("gbk"))
		key = key.strip()
		if key == "": continue
		if key in ("1", "2"):
			key = int(key)
		else:
			sys.exit(0);
		break
	main(options, key)
