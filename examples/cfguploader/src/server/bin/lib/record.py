# -*- coding: utf-8 -*-

import time
import fcntl

class Record(object):
	def __init__(self, path):
		self.__path = path
		self.__file = None
		self.__user = None

	def __print(self, key, msg, *args):
		dtime = time.strftime("%Y-%m-%d %H:%M:%H")
		if self.__user is None:
			self.__file.write("[%s][%s]: %s\n" % (key, dtime, msg % args))
		else:
			self.__file.write("[%s][%s][user=%s]: %s\n" % (key, dtime, self.__user, msg % args))

	def capture(self, addr):
		self.__file = open(self.__path, "a")
		fcntl.flock(self.__file, fcntl.LOCK_EX)
		self.__file.write("# " + "-" * 90 + "\n")
		self.__file.write("# accept a net connection from: %s:%d\n" % addr)
		self.__file.write("# " + "-" * 90 + "\n")

	def setuser(self, user):
		self.__user = user

	def debug(self, msg, *args):
		self.__print("DEBUG", msg, *args)

	def error(self, msg, *args):
		self.__print("ERROR", msg, *args)

	def release(self):
		if self.__file is not None:
			self.__file.write("\n")
			self.__file.close()
			self.__file = None

