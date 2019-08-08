# -*- coding: utf-8 -*-


"""
实现 python 字典配置写入

2010.10.27: writen by huangyongwei
"""

from encode import script2sys

class WriteInfo(object):
	def __init__(self, srcCoding, cpsCoding, cb):
		self.srcCoding = srcCoding
		self.cpsCoding = cpsCoding
		self.layer = 0
		self.__progress = 0.0
		self.__cb = cb

	def _setProgress(self, value):
		self.__progress = value
		cb = self.__cb
		if callable(cb):
			cb(value)
	progress = property(lambda self: self.__progress, _setProgress)


CODINGS = ('utf-8', 'gbk', 'gb18030', 'gb2312', 'ANSII', 'big5')

class Writer(object):
	HEADER		= "# -*- coding: %s -*-%sdatas="

	def __init__(self, coding='utf-8', maxWrapLayer=0, nl="\n"):
		assert coding in CODINGS, "only support encoings: %r" % CODINGS
		self.__typeWriter = {
			dict: Writer.writeDict_,
			tuple: Writer.writeTuple_,
			list: Writer.writeList_,
			int: Writer.writeInt_,
			long: Writer.writeInt_,
			float: Writer.writeFloat_,
			str: Writer.writeStr_,
			unicode: Writer.writeStr_,
			bool: Writer.writeBool_,
			}

		self.__maxWrapLayer = maxWrapLayer
		self.__header = self.HEADER % (coding, nl)
		self.__coding = coding						# 输出编码（生成的配置文件编码）
		self.__srcCoding = coding						# 源文本编码
		self.__nl = self.__nl								# 换行

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __writeText(file, text, percent, writeInfo):
		text = text.replace("\n", "\\n").replace("\r", "\\r")
		file.write('"' + text + '"')
		writeInfo.progress += percent


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def writeDict_(self, file, dct, percent, writeInfo):
		file.write("{")
		layer = writeInfo.layer
		wrap = layer <= self.__maxWrapLayer
		if wrap: file.write(self.__nl + "\t" * (layer + 1))
		count = len(dct)
		if count > 0:
			writeInfo.layer += 1
			perPercent = percent * 0.5 / count
			for key, value in dct.iteritems():
				self.__typeWriter[type(key)](self, file, key, perPercent, writeInfo)
				file.write(": ")
				self.__typeWriter[type(value)](self, file, value, perPercent, writeInfo)
				file.write(", ")
				if wrap: file.write(self.__nl + "\t" * (layer + 1))
			writeInfo.layer -= 1
		file.write("}")

	def writeTuple_(self, file, array, percent, writeInfo):
		file.write("(")
		count = len(array)
		if count > 0:
			perPercent = percent / count
			for elem in array:
				self.__typeWriter[type(elem)](self, file, elem, perPercent, writeInfo)
				file.write(", ")
		file.write(")")

	def writeList_(self, file, array, percent, writeInfo):
		file.write("[")
		count = len(array)
		if count > 0:
			perPercent = percent / count
			for elem in array:
				self.__typeWriter[type(elem)](self, file, elem, perPercent, writeInfo)
				file.write(", ")
		file.write("]")

	def writeInt_(self, file, value, percent, writeInfo):
		file.write(str(value))
		writeInfo.progress += percent;

	def writeFloat_(self, file, value, percent, writeInfo):
		file.write(str(value))
		writeInfo.progress += percent;

	def writeStr_(self, file, value, percent, writeInfo):
		srcCoding = writeInfo.srcCoding
		cpsCoding = writeInfo.cpsCoding
		if cpsCoding == self.__coding:				# 输入压缩编码和输出编码一致
			self.__writeText(file, value, percent, writeInfo)
		else:
			if cpsCoding is not None:					# 输入有压缩编码
				value = value.decode(cpsCoding)		# 解压得出原始编码，即 srcCoding
			if srcCoding != self.__coding:
				value = value.encode(self.__coding)
			self.__writeText(file, value, percent, writeInfo)

	def writeBool_(self, file, value, percent, writeInfo):
		file.write("True" if value else "False")
		writeInfo.progress += percent


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def write(self, path, dct, srcCoding="gb18030", cpsCoding=None, cb=None):
		"""
		@param			path     : 要保存的路径
		@param			dct      : 要写出的字典
		@param			srcCoding: 文本的编码方式（通常为工程的本地语言编码方式）
		@param			cpsCoding: 字典中文本的当前压缩编码（没压缩的话是 None）
		@param			cb       : 进度回调，包含一个小于 1.0 的参数表示当前写出进度
		"""
		assert srcCoding in CODINGS, "only support encoings: %r" % CODINGS
		path = script2sys(path)
		try:
			file = open(script2sys(path), 'w')
		except Exception, err:
			print "open file error:" + self.__nl + "\t" + err
		else:
			try:
				print "begin writing '%s' ..." % path
				file.write(self.__header)
				info = WriteInfo(srcCoding, cpsCoding, cb)
				self.writeDict_(file, dct, 1.0, info)
				file.close()
				print "end writing '%s'..." % path
			except Exception, err:
				file.close()
				raise err
