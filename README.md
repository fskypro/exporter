# exporter
table exporter implemented by python

# -*- coding: utf-8 -*-
#

"""
导出模版说明

tpl_base 中的属性：
	1、DECIMAL_DIGITS: 浮点数后面保留的位数（可在本模块中覆盖）
	2、endCode: 结束代码，即在配置字典结束后，可以加入一段 python 的代码（可在本模块中覆盖）

tpl_base 中的函数：
	1、getExcelRoot(): 获取导出的 EXCEL 文件所在路径的根
	2、getExportTips(): 导出提示

# -----------------------------------------------------
explainer 中的内容获取器：
	一、获取器抽象基类 ex_base(self, defValue=ex_base.INNER)，所有获取器都必需继承于该类，该类不能实例化。

	二、ex_col_base(key, defValue=ex_base.INNER): 获取器基类，参数：① 列头名；② 默认值
		ex_col_base 中有两个保护成员函数：
		1、getColIndex_() 返回以 0 开始的行索引
		2、self.getCellText_(row) 返回当前列指定行的格子内容

	三、可实例化列映射获取器（继承于 ex_col_base，必需对应一个列）
		1、ex_orign_col(key)：直接返回当前格子内容
		2、ex_str_col(key, defValue=ex_base.INNER)：字符串格式
		3、ex_bool_col(key, defValue=False)：布尔型
			注意：该类存在属性：trueSigns_ 和 falseSigns_ 这两属性是一个元组，分别表示 excel 表格中表示布尔型的“真”与“假”的代号，
				它可以被子类对象修改，如：self.trueSigns_ = ("T", "TRUE")，这样 excel 表格中填写“T”或 “TRUE”时，则被解释为“真”。
				它对应 config.xml 表格中的 <explainer>/<trueSigns> 和 <explainer>/<falseSigns>。也可以在模板开头被设置，如：
				CustomConfig.setTrueSigns("T", "TRUE")，如果不设置，将会使用 config.xml 中配置的符号表示布尔型。
		4、ex_int_col(key, defValue=0)：整型格式
		5、ex_hlint_col(key, defValue=0x0, sites=0)：十六进制整型/长整型格式
		6、ex_float_col(key, defValue=0.0)：浮点格式
		7、ex_str_array_col(key, ecount=0, defValue=ex_base.INNER)：字符串元组格式。（Excel 中填表时以英文“,”号隔开）
			trim 表示是否去每个元素前后的空格
			假设 defValue 为：("A", "B", "C")，则：
				Excel 对应格填写的内容为空，则结果为：("A", "B", "C")
				Excel 对应格填写的内容为：11;22，则结果为：("11", "22")
				Excel 对应格填写的内容为：11;;33，则结果为：("11", "", "33")
				Excel 对应格填写的内容为：11; ;33，则结果为：trim == True 时为：("11", "", "33")；trim == False 时为：("11", " ", "33")
				Excel 对应格填写的内容为：11; 22，则结果为：("11", " 22")
				Excel 对应格填写的内容为：11;22;33;44，则结果为：("11", "22", "33", "44")
			假设不传入默认值，则：
				Excel 对应格填写的内容为空，则结果为：()
			注意：ex_str_array_col 具有 splitter_ 属性，可以在子类中修改它。该属性表示元组在 excel 表格中的元素分隔符，它对应 config.xml 中设置的
				<explainer>/<splitter> 分隔符，它也可以在每个模板的开头设置。
		8、ex_int_array_col(key, ecount=0, defValue=ex_base.INNER)：整型元组格式。（Excel 中填表时以英文“,”号隔开）
			假设 defValue 为：(11, 22, 33)，则：
				Excel 对应格填写的内容为空，则结果为：(11, 22, 33)
				Excel 对应格填写的内容为：7; 8，则结果为：(7, 8)
				Excel 对应格填写的内容为：7; ;9，则结果为：(7, 22, 9)
				Excel 对应格填写的内容为：7;8，则结果为：(7, 8)
				Excel 对应格填写的内容为：7;8;9 ;10，则结果为：(7, 8, 9, 10)
			假设不传入默认值，则：
				Excel 对应格填写的内容为空，则结果为：()
				Excel 对应格填写的内容为：7;;8，这样将无法解释第二个元素，结果将会导致导出失败
			注意：ex_str_array_col 具有 splitter_ 属性，可以在子类中修改它。该属性表示元组在 excel 表格中的元素分隔符，它对应 config.xml 中设置的
				<explainer>/<splitter> 分隔符，它也可以在每个模板的开头设置。
		9、ex_hlint_array_col(key, ecount=0, defValue=ex_base.INNER, sites=0)：十六进制整型/长整型元组格式。（Excel 中填表时以英文“,”号隔开）
			假设 defValue 为：(11, 22, 33)，则：
				Excel 对应格填写的内容为空，则结果为：(11, 22, 33)
				Excel 对应格填写的内容为：7; 8，则结果为：(7, 8)
				Excel 对应格填写的内容为：7; ;9，则结果为：(7, 22, 9)
				Excel 对应格填写的内容为：7;8，则结果为：(7, 8)
				Excel 对应格填写的内容为：7;8;9 ;10，则结果为：(7, 8, 9, 10)
			假设不传入默认值，则：
				Excel 对应格填写的内容为空，则结果为：()
				Excel 对应格填写的内容为：7;;8，这样将无法解释第二个元素，结果将会导致导出失败
			注意：ex_str_array_col 具有 splitter_ 属性，可以在子类中修改它。该属性表示元组在 excel 表格中的元素分隔符，它对应 config.xml 中设置的
				<explainer>/<splitter> 分隔符，它也可以在每个模板的开头设置。
		10、ex_float_array_col(key, ecount=0, defValue=ex_base.INNER)：浮点型元组格式。（Excel 中填表时以英文“,”号隔开）
			假设 defValue 为：(11.0, 22.0, 33.0)，则：
				Excel 对应格填写的内容为空，则结果为：(11.0, 22.0, 33.0)
				Excel 对应格填写的内容为：7.0; 8.0，则结果为：(7.0, 8.0)
				Excel 对应格填写的内容为：7.0; ;9.0，则结果为：(7.0, 22.0, 9.0)
				Excel 对应格填写的内容为：7.0;8.0，则结果为：(7.0, 8.0)
				Excel 对应格填写的内容为：7.0;8.0;9.0 ;10.0，则结果为：(7.0, 8.0, 9.0, 10.0)
			假设不传入默认值，则：
				Excel 对应格填写的内容为空，则结果为：()
				Excel 对应格填写的内容为：7.0;;8.0，这样将无法解释第二个元素，结果将会导致导出失败
			注意：ex_str_array_col 具有 splitter_ 属性，可以在子类中修改它。该属性表示元组在 excel 表格中的元素分隔符，它对应 config.xml 中设置的
				<explainer>/<splitter> 分隔符，它也可以在每个模板的开头设置。
		11、ex_multitype_array_col(key, defValues)：联合类型元组格式，etypes 为元组中每个元素的默认值（支持类型：str/bool/int/hlint/float）
			注意：这个必需传入默认值，解释器会根据默认值中每个元素的类型来解释 Excel 表格对应格子的内容。
				并且导出的元素个数必然为默认值中的元素个数。如果 Excel 表格中对应的格子填写的个数不够，则会从默认值中抽取。
			假设 defValue 为：("aa", 11, 22.0, hlint(33))，则：
				Excel 对应格填写的内容为空，则结果为：("aa", 11, 22.0, hlint(33))
				Excel 对应格填写的内容为：7;7;9;10，则结果为："7";8;9.0;hlint(10)
				Excel 对应格填写的内容为：7;8，则结果为："7", 8, 22.0, hlint(33)
				Excel 对应格填写的内容为：7;;9，则结果为："7", 11, 9.0, hlint(33)
			注意：ex_str_array_col 具有 splitter_ 属性，可以在子类中修改它。该属性表示元组在 excel 表格中的元素分隔符，它对应 config.xml 中设置的
				<explainer>/<splitter> 分隔符，它也可以在每个模板的开头设置。
		12、ex_scale_col(key)：默认值为 1.0 的浮点解释器

		13、ex_key_int_col(key)：整型字典键（只能用于最外层－－类型不正确，则整行被忽略掉）
		14、ex_key_hlint_col(key, sites=0)：十六进制整型/长整型字典键（只能用于最外层－－类型不正确，则整行被忽略掉）
			sites 是十六进制的位数，如：hlint(0x2, 4) 则显示为：0x0002
		15、ex_key_tuple_col(key, types)：元组最外层字典键，types 为元组中每个元素的分别类型，支持的类型有：str/bool/int/hlint/
			注意：ex_str_array_col 具有 splitter_ 属性，可以在子类中修改它。该属性表示元组在 excel 表格中的元素分隔符，它对应 config.xml 中设置的
				<explainer>/<splitter> 分隔符，它也可以在每个模板的开头设置。

	四、可实例化非列映射获取器（继承于 ex_base，可以不对应任何列）
		1、ex_key_row(offset=0)：以列号作为字典键，offset 为列号偏移值，假如 offset == -5，则第五行 key 值为 0
		2、ex_key_cols((key, ktype), (key1, ktype1), ...)：多列组成的元组为最外层字典键

	五、获取器成员函数：
		1、__call__(self, dsrc, row) 必需返回：
			① KEYRET_EMPTY				键返回此值表示该行键为空
			② KEYRET_IGNOR				键返回此值表示该行忽略（不导出）
			③ 返回具体键值
			返回 ① 表示 excel 表格中该行的键为空，将不会导出，并在导出成功后的控制台中提示该行为空（因为有可能是填漏的）
			返回 ② 表示 excel 表格中该行是故意忽略（不导出）的，因此在导出成功后不会提示，该值结合 cfg_base 中的“IGNOR_KEY”使用，
				IGNOR_KEY 在 config.xml 中由用户自定义。假如 config.xml 中 <explainer>/<ignorSign> 定义为“unexport”，并且 excel 表中某行的
				键填写为“unexport”，则在导出表格时，该行将会被忽略（不导出），并且在导出结束后不会提示。
				注意：
					A. 只有最外层键列才起作用，其他列填写该值将作正常数据处理
					B. 如果 config.xml 中 <explainer>/<ignorSign> 定义为空，则意味着所有空行都将忽略，并且不会提示。
					C. ex_key_cols 多列组成的键，只要其中一列标记为“unexport”，则该行都会被忽略
			④ 解释出错可以抛出一个异常：
				import Printer
				raise Printer.ExplainException(提示信息)

# -----------------------------------------------------
explainer 中增加的基本类型：
	hlint：十六进制整型/长整型，构造函数：hint(value=0, sites=0)，site 表示显示的位数，如果实际值小于位数，则按实际值为准。
		例如：hlint(10) == 10；hlint(0x10) == 0xa；hlint("0x10") == 0xa；hlint("10") == 10
			hlint(0x10, 6) 显示为：0x00010；hlint(0x1234567, 2) 显示为：0x1234567

config 中的成员：
	from TableExporter import CustomConfig()
	1、可读写属性（config.xml）
		sysConfig.pyHeader：对应 config.xml 中的：<pyheader>
			写出到 python 配置中的头，通常为：# -*- coding: utf-8 -*-\n#\n，可以被模板修改
		CustomConfig().sysEncoding 对应 bin.xml 中的：<sysEncoding>
			运行该软件的系统编码
		CustomConfig().srcEncoding：对应 config.xml 中的：<encodings>/<srcEncoding>
			Excel 编码，也就是 excel 文件中文本的编码，可以被模板修改
		CustomConfig().dstEncoding：对应 config.xml 中的：<encodings>/<dstEncoding>
			导出到 python 配置中的编码，可以被模板修改

		CustomConfig().trueSigns：对应 config.xml 中的：<explainer>/<trues>
			True 布尔变量的表示方式，可以被模板修改，
		CustomConfig().setTrueSigns(*signs)
			CustomConfig().setTrueSigns("true", "True", "T")，这样，在 Excel 表格中填写 “true”或“True”或“T”则表示为 true
		CustomConfig().falseSigns：对应 config.xml 中的：<explainer>/<falses>
			False 布尔变量的表示方式，可以被模板修改
		CustomConfig().setFalseSigns(*signs)
			CustomConfig().setFalseSigns("false", "False", "F")，这样，在 Excel 表格中填写 “false”或“False”或“F”则表示为 false
		CustomConfig().ignorSign：对应 config.xml 中的：<explainer>/<ignorSign>
			可以被模板修改
		CustomConfig().arrSpliter 对应 config.xml 中的：<explainer>/<arrSpliter>
			可以被模板修改

	2、方法：
		CustomConfig().query(key, vtype)
			通过该方法可以读取 config.xml 中的一个段中的标签。用户也可以自己在 config.xml 中添加一个标签，如：
			<user>
				<key> value </key>
			</user>
			则，在模板中可以通过 CustomConfig().query("user/key") 来获取字符串“value”。
			如果 config.xml 中不存在这些标签，则会返回 None

Printer 中的可用成员：
	① ExplainException(msg) 异常
		解释失败可以抛出一个 ExplainException 异常，msg 为错误提示内容

	② ExplainErrorValueTypeException(table, row, colName) 异常
		excel 表格中填写的值类型不正确时，可以抛出该异常
		row 为行索引（第一行为 0）
		colName 为列名

	③ dmsg(*msgs) 函数，导出完毕后，控制台上输出一个字符串，然后换行
		通常可以用该函数输出一个警告。例如，警告：XX 格子内容填写不正确。
		注意：msgs 参数必须为“utf-8”编码

	④ catmsg(*msgs) 函数，与 dmsg 一样，只是打印后不会自动换行。
		如：catmsg("AA", "xx")
			catmsg(" BB", "yy")
		输出为：AA, xx BB, yy
		注意：msgs 参数必须为“utf-8”编码

Path 模块中的成员：
	① normalizePath(path) 标准化一个路径
		如：path = "abc\\def///ghi/../jkl\\mnl.xml"
		调用:
		from libs import Path
		path = Path.normalizePath(path)
		后，path 变为："abc\\def\\jkl\\mnl.xml"

	② executeDirectory() 返回 excel2py.exe 的所在路径（文本编码与 python 脚本编码一致）

# -----------------------------------------------------
注意：
	① 获取器中的 __call__ 函数参数的行是以 0 开始的（即：第一行为 0）。而 Excel 中是以 1 开始的，因此如果
		要输出提示某行某列不正确之类的，则需要对行号加 1。
	② Table 中有静态成员函数：col2CharsCol(col) 可以将以 0 开头的列号转换为 Excel 表格中以字母表示的列号。
		如，第 27 列转换：
			import Table
			Table.col2CharsCol(26)		# 结果为“AA”
		在 __call__ 函数中，可以通过参数 table 来调用 col2CharsCol，而不需要 import Table
		如，第 29 列转换：
			table.col2CharsCol(28)		# 结果为“AC”
	③ 所有信息答应都不要用 print，应该用 dmsg 或 catmsg，这两个函数用法看上面。
"""

from explainer import *
from tpl_base import *

# --------------------------------------------------------------------
# 解释函数列表
# --------------------------------------------------------------------
class f_modelid(ex_key_int_col):
	def __init__(self, key):
		ex_key_int_col.__init__(self, key)


	def __call__(self, dsrc, row):
		"""
		可以引起以下异常：
		raise ExplainException(提示信息)
		"""
		text = self.getCellText_(row)
		if text == "": return KEYRET_EMPTY
		if text == bin.ignorSign: return KEYRET_IGNOR
		mid = ex_key_int_col(self, dsrc, row)
		if mid < 0:
			raise ExplainException("第 %s 列的“模型ID”不能是负数。" % dsrc.col2CharsCol(table))
		return mid

class f_act(ex_multitype_array_col):
	def __init__(self, key):
		ex_multitype_array_col.__init__(self, key, (str, float) ("", 0.0))

class ex_scale_col(ex_float_col):
	def __init__(self, key):
		ex_float_col.__init__(self, key, 1.0)

	def __call__(self, dsrc, row):
		"""
		可以引起以下异常：
		raise ExplainException(提示信息)
		"""
		return ex_float_col.__call__(self, dsrc, row)


# --------------------------------------------------------------------
# 导出格式设置
# --------------------------------------------------------------------
sheet = SheetInfo(
	getExcelRoot() + r"design\BaseData\程序用数据表\道具装备\C_武器_客户端.xlsx",
	"武器模型",
	0, 1)

exp = {f_modelid("武器模型ID", 4):
	{"src": ex_orign_col("模型名"), "px1": ex_str_array_col("初始特效1", ("", "")), "px2": ex_str_array_col("初始特效2", ("", "")),
	hlint(0x40): {"hpHold": ex_orign_col("左手持挂点"), "hpHang": ex_orign_col("左手收挂点"), "actHold": f_act("左手取下动作"), "actHang": f_act("左手收起动作")},
	hlint(0x41): {"hpHold": ex_orign_col("右手持挂点"), "hpHang": ex_orign_col("右手收挂点"), "actHold": f_act("右手取下动作"), "actHang": f_act("右手收起动作")},
	"scales": {hlint(0x100): ex_scale_col("人族比例"), hlint(0x200): ex_scale_col("精灵比例"), hlint(0x300): ex_scale_col("影魔比例"), hlint(0x400): ex_scale_col("多多利比例"), hlint(0x500): ex_scale_col("兽人比例")}
	}}

expInfo = ExpInfo(sheet, exp)
tips = getExportTips() % (sheet.path, sheet.name)

dicts = [
	CfgElem("datas", (tips, (expInfo, )),
	]

# 下面这样可以在导出完毕后，执行一个回调
def func(datas):
	"""
	datas 为最终导出的配置字典数据
	"""
	pass

dicts = (
	CfgElem("datas", tips, (expInfo, ), func),
	)


# --------------------------------------------------------------------
# 说明
# --------------------------------------------------------------------
# 一个 datas 由多张表构成
dicts = {
	CfgElem("datas", _tips, (_expInfo0, _expInfo1, ...)),
	}

# 一个配置中多个 datas
dicts = {
	CfgElem("datas0", _tips0, (_expInfo0, )),
	CfgElem("datas1", _tips1, (_expInfo1, )),
	....
	}


# -------------------------------------------
headRow = 0   # 表示为头的行索引（注意：第一行的行索引为 0），如果不写，则默认值为 0
startRow = 1  # 有效数据行的起始行索引，如果不写，则默认值为 1


# -------------------------------------------
# 可以在导出完毕后写入一段 python 代码
endCode = \
"""
# --------------------------------------------------------------------
# python code
# --------------------------------------------------------------------
def func(a, b, c):
	print "结果：", a, b, c
"""
