# -*- coding: utf-8 -*-
#

"""
简单的 XML 读写器


"""

import os
import re
import Path
from custom_types.hlint import hlint
from custom_types.Vectors import Vector2
from custom_types.Vectors import Vector3
from custom_types.Vectors import Vector4
from encode import script2sys

# --------------------------------------------------------------------
# global variables
# --------------------------------------------------------------------
_errTagChars = "<>\\/\n\r"
_reptnErrTagName = re.compile("[%s]" % _errTagChars)	# 错误 tag 名称匹配器
_reptnStartTag = re.compile(
	r"^<([^%s]*)>([^<>]*)" % _errTagChars)				# 匹配起始 tag
_reptnEndTag = re.compile(
	r"^</([^\\<>\n\r]*)>\s*")							# 匹配结束 tag
_reptnOneTagScope = re.compile(
	r"^<([^%s]*/\s*)>\s*" % _errTagChars)				# 匹配 <XXXXX/>
_reptnComment = re.compile(
	r"(?s)^<!--.*?-->\s*")								# 匹配注释

_reptnNewline = re.compile("\r\n|\r|\n")				# 匹配换行

_noteESCs = {
	'<': "&lt;", '>': "&gt;",
	"'": "&apos;", '"': "&quot;",}						# 关键符：转义符
_escNotes = {}											# 转义符：关键符
for note, esc in _noteESCs.iteritems(): _escNotes[esc] = note
_reptnNote2ESC = re.compile("(%s)" % ("|".join(_noteESCs.keys())))
_reptnESC2Note = re.compile("(%s)" % ("|".join(_escNotes.keys())))

_spaceESCs = {
	' ': "&#x20;",
	'\t': "&#x09;",
	'\n': "&#x0a;",
	'\r': "&#x0d;",}									# 空白字符：转义符
_escSpaces = {}											# 转义符：空白字符
for space, esc in _spaceESCs.iteritems(): _escSpaces[esc] = space
_reptnChars = re.compile("&#[xX]([\da-fA-F]+);")		# ansii 字符


# --------------------------------------------------------------------
# inner methods
# --------------------------------------------------------------------
def _encodeESC(text):
	"""
	将文本中的“关键标记”转换为“转义字符”表示
	"""
	return _reptnNote2ESC.sub(lambda m: _noteESCs[m.groups()[0]], text)

def _decodeESC(text):
	"""
	将文本中的“转义字符”还原为“关键标记”
	"""
	return _reptnESC2Note.sub(lambda m: _escNotes[m.groups()[0]], text)

def _encodeStartEndSpace(text):
	"""
	将字符串两端的空白字符转换为对应的转义字符
	"""
	start = end = ""
	for char in text:
		if char in _spaceESCs:
			start += _spaceESCs[char]
		else:
			break
	text = text.lstrip()
	for index in xrange(len(text)-1, -1, -1):
		char = text[index]
		if char in _spaceESCs:
			end = _spaceESCs[char]
		else:
			break
	return start + text.rstrip() + end

def _decodeChars(text):
	"""
	将用 ansii 编码的字符解码为对应字符
	"""
	def replace(m):
		hvalue = m.groups()[0]
		value = int("0x"+hvalue, 16)
		if value < 256: return chr(value)
		return hvalue
	return _reptnChars.sub(replace, text)


# --------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------
class SXMLException(Exception):
	def __init__(self, msg):
		Exception.__init__(self, script2sys(msg))

# -------------------------------------------
class ErrorXMLException(SXMLException):
	"""
	无效 xml 文件
	"""
	def __init__(self, fileName, lineNo, msg=None):
		self.fileName = fileName
		self.lineNo = lineNo
		premsg = "Error xml file at line: %i" % lineNo
		if msg is None:
			msg = premsg + "!"
		else:
			msg = "%s\n\t%s" % (premsg, msg)
		SXMLException.__init__(self, msg)

class InvalidTagXMLException(ErrorXMLException):
	"""
	无效的 tag
	"""
	def __init__(self, fileName, lineNo, tag):
		self.tag = tag
		msg = "invalid tag: '%s'" % tag
		ErrorXMLException.__init__(self, fileName, lineNo, msg)

class NoEndMarkXMLException(ErrorXMLException):
	"""
	没结束符“>”的 tag
	"""
	def __init__(self, fileName, lineNo, tag):
		self.tag = tag
		msg = "tag '%s' has no end mark '>'" % tag
		ErrorXMLException.__init__(self, fileName, lineNo, msg)

class EmptyTagXMLExceptin(ErrorXMLException):
	"""
	空 tag
	"""
	def __init__(self, fileName, lineNo):
		msg = "contain an empty tag!"
		ErrorXMLException.__init__(self, fileName, lineNo)

class UnmatchTagXMLException(ErrorXMLException):
	"""
	tag 不匹配
	"""
	def __init__(self, fileName, lineNo, start, end):
		self.start = start
		self.end = end
		msg = "Tags do not match: \n\t%s\n\t%s" % \
			("start tag = " + start, "end tag = " + end)
		ErrorXMLException.__init__(self, fileName, lineNo, msg)

class UnterminatedXMLException(ErrorXMLException):
	"""
	没有终结 tag
	"""
	def __init__(self, fileName, lineNo, tag):
		self.tag = tag
		msg = "'%s' has no terminated tag!" % tag
		ErrorXMLException.__init__(self, fileName, lineNo, msg)

class UnstartedXMLException(ErrorXMLException):
	"""
	没有起始的 tag
	"""
	def __init__(self, fileName, lineNo, tag):
		self.tag = tag
		msg = "Unstarted tag: %s!" % tag
		ErrorXMLException.__init__(self, fileName, lineNo, msg)

class ErrorCommentXMLException(ErrorXMLException):
	"""
	无效的 xml 注释
	"""
	def __init__(self, fileName, lineNo):
		ErrorXMLException.__init__(self, fileName, lineNo, "error comment!")

# -------------------------------------------
class ErrorTagNameXMLException(SXMLException):
	"""
	错误的 tag 名称
	"""
	def __init__(self, tagName):
		self.tagName = tagName
		msg = "Error xml tag name: %s" % tagName
		SXMLException.__init__(self, msg)

# -------------------------------------------
class FormatValueXMLException(SXMLException):
	"""
	格式化标签值时错误
	"""
	def __init__(self, strValue, vtype):
		msg = "Format error, can't convert '%s' to value of %s" % (strValue, vtype)
		SXMLException.__init__(self, msg)


# --------------------------------------------------------------------
# section base calass
# --------------------------------------------------------------------
class SimpleXMLSection(object):
	class __pause: pass
	class __skip: pass

	def __init__(self, name, layer, value="", fileName=""):
		self.__name = name
		self.__layer = layer
		self.__orignValue = value.strip()
		self.__tmpValue = None
		self.__fileName = fileName
		self.__subSects = []


	# ----------------------------------------------------------------
	# inner methods
	# ----------------------------------------------------------------
	def __getitem__(self, key):
		keys = key.split('/')
		sect = self
		while len(keys):
			key = keys.pop(0)
			if key == "": continue
			finded = False
			for s in sect.__subSects[:]:
				if s.name == key:
					sect = s
					finded = True
					break
			if not finded:
				return None
		return sect

	def __getattribute__(self, name):
		if name.startswith("_SimpleXMLSection__"):
			return object.__getattribute__(self, name)
		try:
			return object.__getattribute__(self, name)
		except AttributeError:
			if name.startswith("_"):
				name = name[1:]
				for sect in self.__subSects:
					if sect.__name == name:
						return sect
			raise AttributeError("'SimpleXMLSection' object has no attribute '_%s'" % name)


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def name(self):
		return self.__name

	@property
	def layer(self):
		return self.__layer

	def _getValue(self):
		return self.__orignValue
	def _setValue(self, value):
		self.__orignValue = value
		self.__tmpValue = None
	__value = property(_getValue, _setValue)

	# -------------------------------------------------
	def _getAsString(self):
		if self.__tmpValue is None:				# 防止每次去取时都进行转换
			value = _decodeESC(self.__value)
			value = _decodeChars(value)
			self.__orignValue = value
			self.__tmpValue = value
		return self.__tmpValue
	def _setAsString(self, value):
		value = _encodeESC(value)
		value = _encodeStartEndSpace(value)
		self.__value = value
	asString = property(_getAsString, _setAsString)

	def _getAsInt(self):
		return SimpleXMLSection.__toInt(self.__value)
	def _setAsInt(self, value):
		if type(value) in (int, long, float, bool, hlint):
			self.__value = str(int(value))
		else:
			raise TypeError("Expected int value.")
	asInt = property(_getAsInt, _setAsInt)

	def _getAsHLInt(self):
		return SimpleXMLSection.__toHLInt(self.__value)
	def _setAsHLInt(self, value):
		if type(value) in (int, long, float, bool, hlint):
			self.__value = str(hlint(value))
		else:
			raise TypeError("Expected int value.")
	asHLInt = property(_getAsHLInt, _setAsHLInt)

	def _getAsFloat(self):
		return SimpleXMLSection.__toFloat(self.__value)
	def _setAsFloat(self, value):
		if type(value) in (float, int, long, bool):
			self.__value = str(float(value))
		else:
			raise TypeError("Expected float value.")
	asFloat = property(_getAsFloat, _setAsFloat)

	def _getAsBool(self):
		return SimpleXMLSection.__toBool(self.__value)
	def _setAsBool(self, value):
		if type(value) in (bool, int, long, float):
			self.__value = str(bool(value))
		else:
			raise TypeError("Expected boolean value.")
	asBool = property(_getAsBool, _setAsBool)

	def _getAsVector2(self):
		return SimpleXMLSection.__toVector(self.__value, 2)
	def _setAsVector2(self, value):
		if len(value) != 2:
			raise TypeError("Expected tuple with 2 float elements.")
		for e in value:
			if type(e) not in (float, int, long, bool):
				raise TypeError("Expected tuple with 2 float elements.")
		self.__value = ' '.join(value)
	asVector2 = property(_getAsVector2, _setAsVector2)

	def _getAsVector3(self):
		return SimpleXMLSection.__toVector(self.__value, 3)
	def _setAsVector3(self, value):
		if len(value) != 3:
			raise TypeError("Expected tuple with 3 float elements.")
		for e in value:
			if type(e) not in (float, int, long, bool):
				raise TypeError("Expected tuple with 3 float elements.")
		self.__value = ' '.join(value)
	asVector3 = property(_getAsVector3, _setAsVector3)

	def _getAsVector4(self):
		return SimpleXMLSection.__toVector(self.__value, 4)
	def _setAsVector4(self, value):
		if len(value) != 4:
			raise TypeError("Expected tuple with 4 float elements.")
		for e in value:
			if type(e) not in (float, int, long, bool):
				raise TypeError("Expected tuple with 4 float elements.")
		self.__value = ' '.join(value)
	asVector4 = property(_getAsVector4, _setAsVector4)


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __toInt(text):
		if text == "" or text is None:
			return 0
		try:
			return int(text)
		except:
			raise FormatValueXMLException(text, int)

	@staticmethod
	def __toHLInt(text):
		if text == "" or text is None:
			return hlint()
		try:
			return hlint(text)
		except:
			raise FormatValueXMLException(text, hlint)

	@staticmethod
	def __toFloat(text):
		if text == "" or text is None:
			return 0.0
		try:
			return float(text)
		except:
			raise FormatValueXMLException(text, float)

	@staticmethod
	def __toBool(text):
		if text == "" or text is None:
			return False
		if text.lower() == "true": return True
		if text.lower() == "false": return False
		if text.isdigit(): return bool(int(text))
		try: return bool(float(text))
		except: return False

	@staticmethod
	def __toVector(text, unit):
		clsVectors = {2: Vector2, 3: Vector3, 4: Vector4}
		if text is None:
			return clsVectors[unit](*([0.0]*unit))
		elems = text.split()
		if len(elems) != unit:
			raise FormatValueXMLException(text, "Vector%i" % unit)
		for idx, e in enumerate(elems[:]):
			try: elems[idx] = float(e)
			except: raise FormatValueXMLException(text, "Vector%i" % unit)
		return clsVectors[unit](*elems)

	# -------------------------------------------------
	def __writeXMLCode(self, file):
		if len(self.__subSects):
			if self.__value == "":
				file.write("%s<%s>\n" % ('\t'*self.__layer, self.__name))
			else:
				file.write("%s<%s>\t%s\n" % ('\t'*self.__layer, self.__name, self.__value))
			for sect in self.__subSects:
				sect.__writeXMLCode(file)
			file.write("%s</%s>\n" % ('\t'*self.__layer, self.__name))
		else:
			if self.__value == "":
				file.write("%s<%s>\t" % ('\t'*self.__layer, self.__name))
			else:
				file.write("%s<%s>\t%s\t" % ('\t'*self.__layer, self.__name, self.__value))
			file.write("</%s>\n" % self.__name)


	# ----------------------------------------------------------------
	# friends for SimpleXML
	# ----------------------------------------------------------------
	def __addSubSection__(self, sect):
		self.__subSects.append(sect)


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def keys(self):
		return [e[0] for e in self.__subSects]

	def values(self, tagName=None):
		if tagName is None:
			return [e[1] for e in self.__subSects]
		sects = []
		for sect in self.__subSects:
			if sect.__name == tagName:
				sects.append(sect)
		return sects

	def items(self):
		return [(sect.__name, sect) for sect in self.__subSects]

	def iterkeys(self):
		for sect in self.__subSects:
			yield sect.__name

	def itervalues(self):
		for sect in self.__subSects:
			yield sect

	def iteritems(self):
		for sect in self.__subSects:
			yield (sect.__name, sect)

	def hastag(self, key):
		return self[key] is not None


	# ------------------------------------------------
	# readers
	# ------------------------------------------------
	def readString(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asString
		return ""

	def readInt(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asInt
		return 0

	def readHLInt(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asHLInt
		return 0

	def readFloat(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asFloat
		return 0.0

	def readBool(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asBool
		return False

	def readVector2(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asVector2
		return (0.0, 0.0)

	def readVector3(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asVector3
		return (0.0, 0.0, 0.0)

	def readVector4(self, sname):
		for sect in self.__subSects:
			if sname == sect.__name:
				return sect.asVector4
		return (0.0, 0.0, 0.0, 0.0)

	# ---------------------------------------
	def readStrings(self, sname):
		strs = []
		for sect in self.__subSects:
			if sname == sect.__name:
				strs.append(sect.asString)
		return tuple(strs)

	def readInts(self, sname):
		ints = []
		for sect in self.__subSects:
			if sname == sect.__name:
				ints.append(sect.asInt)
		return tuple(ints)

	def readHLInts(self, sname):
		hlints = []
		for sect in self.__subSects:
			if sname == sect.__name:
				hlints.append(sect.asHLInt)
		return tuple(hlints)

	def readFloats(self, sname):
		floats = []
		for sect in self.__subSects:
			if sname == sect.__name:
				floats.append(sect.asFloat)
		return tuple(floats)

	def readBools(self, sname):
		bools = []
		for sect in self.__subSects:
			if sname == sect.__name:
				bools.append(sect.asBool)
		return tuple(bools)

	def readVector2s(self, sname):
		v2s = []
		for sect in self.__subSects:
			if sname == sect.__name:
				v2s.append(sect.asVector2)
		return tuple(v2s)

	def readVector3s(self, sname):
		v3s = []
		for sect in self.__subSects:
			if sname == sect.__name:
				v3s.append(sect.asVector3)
		return tuple(v3s)

	def readVector4s(self, sname):
		v4s = []
		for sect in self.__subSects:
			if sname == sect.__name:
				v4s.append(sect.asVector4)
		return tuple(v4s)


	# ------------------------------------------------
	# writers
	# ------------------------------------------------
	def writeString(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asString = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asString = value
		self.__subSects.append(sect)
		return sect

	def writeInt(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asInt = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asInt = value
		self.__subSects.append(sect)
		return sect

	def writeHLInt(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asHLInt = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asHLInt = value
		self.__subSects.append(sect)
		return sect

	def writeFloat(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asFloat = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asFloat = value
		self.__subSects.append(sect)
		return sect

	def writeBool(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asBool = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asBool = value
		self.__subSects.append(sect)
		return sect

	def writeVector2(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asVector2 = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asVector2 = value
		self.__subSects.append(sect)
		return sect

	def writeVector3(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asVector3 = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asVector3 = value
		self.__subSects.append(sect)
		return sect

	def writeVector4(self, sname, value):
		for sect in self.__subSects:
			if sname == sect.__name:
				sect.asVector4 = value
				return
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		sect.asVector4 = value
		self.__subSects.append(sect)
		return sect

	# ---------------------------------------
	def writeStrings(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asString = e
			sects.append(sect)
		self.__subSects += sects

	def writeInts(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asInt = e
			sects.append(sect)
		self.__subSects += sects

	def writeHLInts(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asHLInt = e
			sects.append(sect)
		self.__subSects += sects

	def writeFloats(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asFloat = e
			sects.append(sect)
		self.__subSects += sects

	def writeBools(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asBool = e
			sects.append(sect)
		self.__subSects += sects

	def writeVector2s(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asVector2 = e
			sects.append(sect)
		self.__subSects += sects

	def writeVector3s(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asVector3 = e
			sects.append(sect)
		self.__subSects += sects

	def writeVector4s(self, sname, value):
		sects = []
		for e in value:
			if _reptnErrTagName.search(sname):
				raise ErrorTagNameXMLException(sname)
			sect = SimpleXMLSection(sname, self.__layer+1)
			sect.asVector4 = e
			sects.append(sect)
		self.__subSects += sects

	# -------------------------------------------------
	def gothrough(self, sfilter):
		"""
		遍历所有子孙 section，每经过一个 secion，sfilter 都会被调用
		sfilter 必需包含四个参数：
			① section name
			② section
			③ SimpleXMLSection.__skip
			④ SimpleXMLSection.__pause
			如果 sfilter 返回第 ③ 个参数，则 section 被忽略
			如果 sfilter 返回第 ④ 个参数，则退出遍历
		函数返回一个 list，表示遍历后所得的结果
		"""
		sects = []
		queue = [(self.name, self)]
		pause = SimpleXMLSection.__pause
		skip = SimpleXMLSection.__skip
		while len(queue):
			name, sect = queue.pop(0)
			ret = sfilter(name, sect, skip, pause)
			if ret == pause: break
			elif ret != skip: sects.append(ret)
			for s in sect.__subSects:
				queue.append(s)
		return sects

	def createSection(self, sname):
		"""
		创建 section，格式可以是符合文件名的字符串或文件路径
		"""
		if _reptnErrTagName.search(sname):
			raise ErrorTagNameXMLException(sname)
		sect = SimpleXMLSection(sname, self.__layer+1)
		self.__subSects.append(sect)
		return sect

	def deleteSection(self, sname):
		"""
		删除指定名称的 section
		"""
		for sect in self.__subSects:
			if sname == sect.__name:
				self.__subSects.remove(sect)
				break

	def deleteSections(self, sname):
		"""
		删除指定名称的所有子 section
		"""
		count = len(self.__subSects)
		for index in xrange(count-1, -1, -1):
			sect = self.__subSects[index]
			if sname == sect.__name:
				self.__subSects.pop(index)

	def clearSections(self):
		"""
		清除所有子 section
		"""
		self.__subSects = []

	# -------------------------------------------------
	def save(self):
		if self.__fileName == "":
			raise IOError("save fail. only file section can be saved!")
		file = open(script2sys(self.__fileName), 'w')
		try:
			self.__writeXMLCode(file)
		except Exception, err:
			raise err
		finally:
			file.close()


# ------------------------------------------------------------------------------
# SimpleXML，简单的类 XML 序列化器
# 	① 不支持属性
# 	② 不支持 <XXXXX/> 形式的 XML 标记
# 	③ 支持非 XML 格式文本，通过 _FileSection::asBinary 获取文本内容
# ------------------------------------------------------------------------------
class SimpleXML(object):
	def __init__(self, root=""):
		self.__root = Path.normalizePath(root)
		self.__cache = {}


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@staticmethod
	def __createFile(path, fileName=""):
		"""
		创建文件夹，并返回文件夹或文件路径
		"""
		sysPath = script2sys(path)
		if not os.path.isdir(sysPath):
			os.makedirs(sysPath)
		return os.path.join(path, fileName)

	# -------------------------------------------------
	@staticmethod
	def __getLineCount(text, pointer):
		text = text[:pointer]
		return len(_reptnNewline.findall(text)) + 1

	@staticmethod
	def __explain(fileName, text):
		"""
		解释 XML 文本
		"""
		text = text.strip()
		if text == "":
			path, name = os.path.split()
			return SimpleXMLSection(name, 0, "", fileName)
		elif text.startswith("\xef\xbb\xbf"):				# 签名 utf-8 头
			text = text[3:]
		if not text.startswith("<"):
			raise ErrorXMLException(fileName, 1)

		orign = text
		pointer = 0
		root = None
		sects = []
		while(True):
			if text == "": break
			if text.startswith("<!--"):
				m = _reptnComment.search(text)
				if m is None:
					lineNo = SimpleXML.__getLineCount(orign, pointer)
					raise ErrorCommentXMLException(fileName, lineNo)
				pointer += m.end()
				text = text[m.end():]
			elif text.startswith("</"):													# 结束标记
				if len(sects) == 0:														# 没有起始标记的结束标记
					tag = re.search("^[^%s]*" % _errTagChars, text[2:])					# 找出该没起始 tag 的结束 tag
					lineNo = SimpleXML.__getLineCount(orign, pointer)
					raise UnstartedXMLException(fileName, lineNo, tag.group())
				m = _reptnEndTag.search(text)
				if m is None:															# 错误的结束标记
					lineNo = SimpleXML.__getLineCount(orign, pointer)
					raise UnterminatedXMLException(fileName, lineNo, sects[-1].name)
				tag = m.groups()[0]
				if tag == sects[-1].name:												# 去掉一个嵌套
					sects.pop()
					index = m.end()
					pointer += index
					text = text[index:]
					if len(sects) == 0: break
				else:																	# 结束 tag 与起始 tag 不一致
					lineNo = SimpleXML.__getLineCount(orign, pointer)
					raise UnmatchTagXMLException(fileName, \
						lineNo, sects[-1].name, tag)
			elif text.startswith("<"):													# 起始标记
				m = _reptnStartTag.search(text)
				if m is not None:														# 寻找开始 tag
					tag = m.groups()[0]
					if tag == "":														# 空 tag
						lineNo = SimpleXML.__getLineCount(orign, pointer)
						raise EmptyTagXMLExceptin(fileName, lineNo)
					layer = len(sects)
					if layer:
						sect = SimpleXMLSection(tag, layer, m.groups()[1])
						sects[-1].__addSubSection__(sect)
					else:
						sect = root = SimpleXMLSection(tag, 0, m.groups()[1], fileName)
					sects.append(sect)
					index = m.end()
					pointer += index
					text = text[index:]
				else:
					m = _reptnOneTagScope.search(text)
					if m is not None:
						tag = m.groups()[0]
						if tag == "":													# 空 tag
							lineNo = SimpleXML.__getLineCount(orign, pointer)
							raise EmptyTagXMLExceptin(fileName, lineNo)
						layer = len(sects)
						if layer:
							sect = SimpleXMLSection(tag, layer)
							sects[-1].__addSubSection__(sect)
						else:
							sect = root = SimpleXMLSection(tag, 0, "", fileName)
						index = m.end()
						pointer += index
						text = text[index:]
					else:																# 不是合法的开始 tag
						tag = re.search("^[^%s]*" % _errTagChars, text[1:])				# 找出该不合法的开始 tag
						lineNo = SimpleXML.__getLineCount(orign, pointer)
						raise NoEndMarkXMLException(fileName, lineNo, tag.group())
			else:																		# 标记以外的内容错误
				lineNo = SimpleXML.__getLineCount(orign, pointer)
				m = re.search("^[^\r\n]*", text)
				if m is None:
					raise ErrorXMLException(fileName, lineNo, "invalid xml file!")
				raise InvalidTagXMLException(fileName, lineNo, m.group())

		if len(sects):
			lineNo = SimpleXML.__getLineCount(orign, pointer)
			raise UnterminatedXMLException(fileName, lineNo, sects[-1].name)
		if text != "":
			lineNo = SimpleXML.__getLineCount(orign, pointer)
			raise ErrorXMLException(fileName, lineNo)
		return root


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	@property
	def root(self):
		return self.__root


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def openSection(self, filePath, create=False):
		filePath = Path.normalizePath(filePath)
		fullPath = os.path.join(self.__root, filePath)
		sect = self.__cache.get(fullPath)
		if sect is None:
			sysFullPath = script2sys(fullPath)
			if os.path.isfile(sysFullPath):
				file = open(sysFullPath, 'r')
				text = file.read()
				file.close()
			elif create:
				path, fileName = os.path.split(fullPath)
				fullPath = self.__createFile(path, fileName)
				text = "<root></root>"
			else:
				raise IOError("xml file '%s' is not exist!" % filePath)
			sect = SimpleXML.__explain(fullPath, text)
			self.__cache[fullPath] = sect
		return sect

	def purge(self, xmlFile):
		filePath = Path.normalizePath(xmlFile)
		self.__cache.pop(filePath, None)
