# -*- coding: utf-8 -*-

import hashlib

class Config(object):
	def __init__(self, conf):
		kvs = {}
		cfgfile = open(conf, "r")
		while True:
			line = cfgfile.readline()
			if not line: break
			keyValue = line.split("=")
			if len(keyValue) != 2: continue
			key, value = keyValue
			key = key.strip()
			value = value.strip()
			kvs[key] = value
		cfgfile.close()

		self.host = kvs["host"]
		self.port = int(kvs["port"])
		self.connects = int(kvs["connects"])
		self.fileroot = kvs["fileroot"]
		self.log = kvs["log"]
		self.cmd = kvs["cmd"]
		self.users = {}

		uname = None
		usersFile = open(kvs["users"], "r")
		while True:
			line = usersFile.readline()
			if not line: break
			info = line.split("=")
			if len(info) != 2: continue
			uname, passwd = info
			uname = uname.strip()
			passwd = passwd.strip()
			md5 = hashlib.md5()
			md5.update(uname + "=" + passwd)
			key = md5.hexdigest()
			self.users[key] = uname
		usersFile.close()

