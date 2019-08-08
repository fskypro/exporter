# -*- coding: utf-8 -*-

import os
import re
import sys
import commands
import glob
import shutil
import time
import struct
import socket
import threading

# local
import config
from config import Config
from record import Record

class SvrCode:
	OK                     = 0		# 正常
	ERR_UNKNOW_ACTION      = 1		# 操作不存在
	ERR_IDENTITY           = 2		# 用户不存在，或密匙不正确
	ERR_SAVE_HISTIRY       = 3		# 无法保存历史文件
	ERR_OPEN_FILE          = 4		# 无法打开并保存上传文件
	ERR_RCV_UPLOAD_INFO    = 5		# 接收文件信息失败
	ERR_UNPACK_UPLOAD_INFO = 6		# 错误的上传信息包
	ERR_DST_FILE_NAME      = 7		# 错误的目标文件名
	ERR_RECV_FILE          = 8		# 接收文件失败
	ERR_SAVE_FILE          = 9		# 无法保存上传文件
	ERR_CMD                = 10		# 行刷新配置命令失败
	NO_HISTORY_FILE        = 11		# 历史文件不存在
	ERR_HISTORY_FILE       = 12		# 无法恢复历史版本文件

def debug(msg, *args):
	msg = msg % args
	print "[DEBUG]:", msg
	record.debug(msg)

def error(msg, *args):
	msg = msg % args
	print "[ERROR]:", msg
	record.error(msg)


# -----------------------------------------------------------------------------
# FileServer
# -----------------------------------------------------------------------------
class Handler(object):
	# 16进制MD5密码|文件名|文件大小
	__HEAD_FORMAT = "!i40s64sL"
	__HEAD_SIZE = struct.calcsize(__HEAD_FORMAT)

	__BUFF_SIZE = 1024
	__HISTORY_COUNT = 20			# 拉取历史记录数

	def __init__(self, client):
		self.__client = client

		self.__action = None		# 动作 0 为刷新配置；1 为拉取历史列表；2 为下载历史文件
		self.__uname = None			# 操作用户名

		self.__fname = None			# 上传文件名
		self.__fext = None			# 上传配置扩展名
		self.__fnameext = None		# 上传配置文件全名
		self.__flen = None			# 上传文件长度

		self.__fpath = None			# 上传配置文件全路径
		self.__file = None			# 上传配置文件流

		record.capture(addr)

	def __del__(self):
		debug("upload receiver thread has released")
		try: record.release()
		except: pass
		self.__client.close()

	# -------------------------------------------------------------------------
	# private
	# -------------------------------------------------------------------------
	# 回复确认信息给客户端
	def __rspConfirm(self, status):
		try:
			self.__client.sendall(struct.pack("!I", status))
		except Exception, err:
			error("send upload information received confirm to client fail: %s", err.message)
			return False
		debug("response status to client: %d", status)
		return True

	# 接收上传文件信息
	def __recvUploadInfo(self):
		try:
			strInfo = self.__client.recv(self.__HEAD_SIZE)
		except Exception, err:
			error("receive upload information fail: %s", err.message)
			return SvrCode.ERR_RCV_UPLOAD_INFO
		try:
			headInfo = struct.unpack(self.__HEAD_FORMAT, strInfo)
		except Exception, err:
			error("unpack upload information fail: %s", err.message)
			return SvrCode.ERR_UNPACK_UPLOAD_INFO

		# 动作
		self.__action = headInfo[0]

		# 密匙认证
		identity = headInfo[1].strip('\00')
		if identity not in config.users:
			error("identity(%s) verify fail!", identity)
			return SvrCode.ERR_IDENTITY
		self.__uname = config.users[identity]
		record.setuser(self.__uname)

		# 要操作的配置文件名（带扩展名）
		self.__fnameext = headInfo[2].strip("\00")
		self.__fname, self.__fext = os.path.splitext(self.__fnameext)
		self.__fname = self.__fname.replace("\\", "/")
		if self.__fname == "" or self.__fext == "":
			error("error dst config file name is not valid: %s", self.__fnameext)
			return SvrCode.ERR_DST_FILE_NAME

		# 上传文件
		if self.__action == 1:
			# 上传文件名规范校验
			# 因为下面要对文件名执行命令，因此这里要对文件名进行校验（文件名只能是字母、数字、下划线）
			# 防止黑客利用文件名组成一个命令，钻漏洞攻击服务器
			if re.search("^[a-zA-Z\d_\.]+?$", self.__fnameext) is None:
				error("error dst config file name: %s", self.__fnameext)
				return SvrCode.ERR_DST_FILE_NAME

			self.__flen = headInfo[3]
			debug("receive and unpack upload information successfully: filename='%s', filelen=%d", self.__fnameext, self.__flen)

		return SvrCode.OK

	# ---------------------------------------------------------------
	# 上传文件
	# ---------------------------------------------------------------
	# 创建上传文件
	def __createFile(self):
		filePath = os.path.join(config.fileroot, self.__fnameext)
		self.__fpath = filePath
		# 创建上传文件
		try:
			self.__file = open(filePath, "w")
		except Exception, err:
			error("create upload file fail: %s", err.message)
			return SvrCode.ERR_OPEN_FILE
		debug("begin new upload file '%s'!", filePath)
		return SvrCode.OK

	# 接收上传文件
	def __recvFile(self):
		debug("begin receive file(length=%d): %s", self.__flen, self.__fnameext)
		try:
			fileSize = self.__flen
			while True:
				if fileSize <= 0: break
				if fileSize > self.__BUFF_SIZE:
					data = self.__client.recv(self.__BUFF_SIZE)
				else:
					data = self.__client.recv(fileSize)
				if not data: break
				self.__file.write(data)
				fileSize -= len(data)
		except Exception, err:
			error("receive file fail: %s" + err.message)
			return SvrCode.ERR_RCV_FILE
		else:
			debug("receive file(%s) successfully!", self.__fnameext)

		# 保存上传文件
		try:
			self.__file.close()
		except Exception, err:
			error("save file fail(%s): %s", self.__fnameext, err.message)
			return SvrCode.ERR_SAVE_FILE

		debug("save upload file(%s) successfully!", self.__fnameext)
		return SvrCode.OK

	# 复制上传文件到历史文件夹
	def __copyToHistory(self):
		# 创建历史文件夹
		historyPath = os.path.join(config.fileroot, self.__fname)
		if not os.path.exists(historyPath): os.mkdir(historyPath)

		# 历史文件名：年月日_时分秒[操作用户名].扩展名
		now = time.time()
		ymd_hms = time.strftime("%Y%m%d_%H%M%S")						# 年月日_时分秒
		msec = "%d" % ((now - int(now)) * 1000)							# 毫秒
		historyName = "%s_%s[%s]%s" % (ymd_hms, msec, self.__uname, self.__fext)
		historyFile = os.path.join(historyPath, historyName)

		debug("begin copy the new file to history folder: %s", historyName)
		try:
			shutil.copyfile(self.__fpath, historyFile)
		except Exception, err:
			error("copy new file to history folder fail: %s", err.message)
		else:
			debug("history file has been saved: %s", historyFile)

	# 处理上传刷新配置动作
	def __flushConfig(self):
		# 创建上传文件
		ret = self.__createFile()
		if not (self.__rspConfirm(ret)): return			# 回复 “创建上传文件” 失败
		if ret != SvrCode.OK: return					# 创建上传文件失败

		# 接收并保存上传文件
		ret = self.__recvFile()
		if (ret != SvrCode.OK):							# 接收并保存上传文件失败
			self.__rspConfirm(ret)
			return
	
		# 将新的配置文件复制到历史记录
		self.__copyToHistory()

		# 执行配置更新命令
		cmd = config.cmd + " \"" + self.__fpath + "\""
		status, output = commands.getstatusoutput(cmd)
		if status != 0:
			ret = SvrCode.ERR_CMD
			error("execute command(%s) fail: %s", cmd, output)
		else:
			debug("excute command '%s' successfully!", cmd)
		self.__rspConfirm(ret)


	# ---------------------------------------------------------------
	# 拉取历史记录
	# ---------------------------------------------------------------
	def __pullHistories(self):
		match = re.compile("\d{8}_\d{6}_\d{3}\[[A-Za-z\d_]+\]\\" + self.__fext)
		historyFolder = os.path.split(self.__fname)[1]
		historyRoot = os.path.join(config.fileroot, historyFolder)

		# 获取历史文件夹下所有文件
		fileNames = []
		for fname in os.listdir(historyRoot):
			if match.search(fname) is not None:
				fileNames.append(fname)
		debug("%d history config files found!", len(fileNames))

		# 排序，最新的放在前面，并且只拉取指定数量的历史记录
		fileNames.sort(reverse=True)
		if len(fileNames) >= self.__HISTORY_COUNT:
			fileNames = fileNames[:self.__HISTORY_COUNT]
		buff = "|".join(fileNames)
		sizeBuff = struct.pack("!I", len(buff))
		buff = sizeBuff + buff
		size = len(buff)
		index = 0
		debug("%d history config file list begin send to client!", len(fileNames))
		try:
			while 1:
				if size <= 0: break
				if size >= self.__BUFF_SIZE:
					data = buff[index:index+self.__BUFF_SIZE]
					self.__client.sendall(data)
				else:
					self.__client.sendall(buff[index:])
				index += self.__BUFF_SIZE
				size -= self.__BUFF_SIZE
		except Exception, err:
			error("send history config file list fail: %s", err.message)
		else:
			debug("%d history config file list has sended to client!", len(fileNames))

		self.__rspConfirm(SvrCode.OK)


	# ---------------------------------------------------------------
	# 恢复历史配置
	# ---------------------------------------------------------------
	def __revertHistory(self):
		historyFile = os.path.join(config.fileroot, self.__fnameext)
		historyFile = historyFile.replace("\\", "/")
		if not os.path.exists(historyFile):
			error("history config file is not exists: %s", self.__fnameext)
			self.__rspConfirm(SvrCode.NO_HISTORY_FILE)
			return
		cfgName = self.__fname.split("/")[1] + self.__fext
		print "111111111", self.__fname
		cfgFile = os.path.join(config.fileroot, cfgName)
		try:
			shutil.copyfile(historyFile, cfgFile)
		except Exception, err:
			error("copy history file fail, %s", err.message)
			self.__rspConfirm(SvrCode.ERR_HISTORY_FILE)
			return

		# 执行配置更新命令
		cmd = config.cmd + " \"" + cfgFile + "\""
		status, output = commands.getstatusoutput(cmd)
		if status != 0:
			error("execute command(%s) fail: %s", cmd, output)
			self.__rspConfirm(SvrCode.ERR_CMD)
		else:
			debug("excute command '%s' successfully!", cmd)
			self.__rspConfirm(SvrCode.OK)


	# -------------------------------------------------------------------------
	# public
	# -------------------------------------------------------------------------
	@staticmethod
	def run(client, addr):
		# 接收操作信息包
		handler = Handler(client)
		ret = handler.__recvUploadInfo()
		if not handler.__rspConfirm(ret): return	# 回复收到 “处理文件信息” 失败
		if ret != SvrCode.OK: return				# 接收 “处理文件信息” 失败

		# 请求上传配置
		if handler.__action == 1:
			debug("action = %d and now begin receive upload config file!", handler.__action)
			handler.__flushConfig()
		# 请求拉取上传记录
		elif handler.__action == 2:
			debug("action = %d and now begin pull the config history list!", handler.__action)
			handler.__pullHistories()
		# 请求恢复旧版本
		elif handler.__action == 3:
			debug("action = %d and now begin revert the old version: %s!", handler.__action, handler.__fnameext)
			handler.__revertHistory()
		# 无效操作
		else:
			error("ivalid action = %d!", handler.__action)
			handler.__rspConfirm(SvrCode.ERR_UNKNOW_ACTION)


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
server = None
config = None
record = None
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "[ERROR]: must indicate the config file!"
	else:
		config = Config(sys.argv[1])
		record = Record(config.log)

		print "[DEBUG]: begin accept a connection ..."
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((config.host, config.port))
		sock.listen(config.connects)
		while True:
			client, addr = sock.accept()
			print "[DEBUG]: -------------------------------------------------------"
			print "[DEBUG]: accept a new connection: addr = %s:%s" % addr
			newThread = threading.Thread(target=Handler.run, args=(client, addr))
			newThread.start()
		print "application end!"

