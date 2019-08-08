# -*- coding: utf-8 -*-

import os
import sys
import hashlib


def main(usersfile, idenfolder):
	try:
		f = open(usersfile, "r")
	except:
		print "can't open file: " + usersfile
		return
	if not os.path.exists(idenfolder):
		try:
			os.mkdir(idenfolder)
		except:
			print "output folder is not exist: " + idenfolder
			return

	while 1:
		line = f.readline()
		if not line: break
		up = line.split("=")
		if len(up) != 2: continue
		uname, passwd = up
		uname = uname.strip()
		passwd = passwd.strip()
		up = uname + "=" + passwd
		md5 = hashlib.md5()
		md5.update(up)
		df = open(idenfolder + "/" + uname + ".key", "w")
		df.write(md5.hexdigest())
		df.close()
	print "done."

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print "must indicate the user/password file and dst folder"
	else:
		main(sys.argv[1], sys.argv[2])

