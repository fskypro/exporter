# -*- coding: utf-8 -*-
#

"""
时间扩展模块。用于扩展 time.time

 records:
 	writen by yongwei-huang -- 2013.05.29
"""

import math
import datetime
import time as _time


# --------------------------------------------------------------------
# time 继承
# --------------------------------------------------------------------
time = _time.time
strftime = _time.strftime
strptime = _time.strptime
daylight = _time.daylight
mktime = _time.mktime
sleep = _time.sleep
localtime = lambda tv=None: _time.localtime(time()) if tv is None else _time.localtime(tv)
ctime = lambda tv=None: _time.ctime(time()) if tv is None else _time.ctime(tv)
gmtime = lambda tv=None: _time.gmtime(time()) if tv is None else _time.gmtime(tv)
timezone = _time.timezone
daylight = _time.daylight

# --------------------------------------------------------------------
# time 扩展
# --------------------------------------------------------------------
# 等价于 python 的 time.time 函数
fnow = _time.time

# 返回当前时间，精确到秒
inow = lambda: int(_time.time())

# 等价于 python 库的 time.localtime 函数
local = localtime

# 计算时分秒
def hms(vt):
	vt = int(vt)
	h = vt / 3600
	m = (vt % 3600) / 60
	return h, m, vt % 60

# --------------------------------------------------------------------
# 输入 1970 年以来秒数的日程换算
# --------------------------------------------------------------------
class vtime:
	@staticmethod
	def year(tv=None):
		"""
		获取指定时间值的所在年份
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return local.tm_year

	@staticmethod
	def mon(tv=None):
		"""
		获取指定时间值的所在月份
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return local.tm_mon

	@staticmethod
	def mday(tv=None):
		"""
		获取指定时间值所在的号
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return local.tm_mday

	@staticmethod
	def ymd(tv=None):
		"""
		获取指定时间所在的年月日
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return local.tm_year, local.tm_mon, local.tm_mday

	# -------------------------------------------------
	@staticmethod
	def wday(tv=None):
		"""
		获取指定时间所在星期
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return local.tm_wday + 1

	@staticmethod
	def yday(tv=None):
		"""
		获取指定时间所在当年的第几天
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return local.tm_yday


	# ----------------------------------------------------------------
	# week in month/year
	# ----------------------------------------------------------------
	@staticmethod
	def mweekth(tv=None):
		"""
		获取指定时间是当月下的第几个星期（顺序为：一、二、三、四、五、六、日。即星期的起始日为周一）
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		year = local.tm_year
		mon = local.tm_mon
		dayIndex = local.tm_mday - 1								# 一号索引
		weekDayIndex_1 = datetime.datetime(year, mon, 1).weekday()	# 一号的星期索引
		return (dayIndex + weekDayIndex_1) / 7 + 1

	@staticmethod
	def yweekth(tv=None):
		"""
		获取指定时间是当年的第几个星期
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		year = local.tm_year
		ydayIndex = local.tm_yday - 1								# 一年的第几天的索引
		weekDayIndex_11 = datetime.datetime(year, 1, 1).weekday()	# 一月一号的星期索引
		return (ydayIndex + (weekDayIndex_11 % 6)) / 7 + 1


	# ----------------------------------------------------------------
	# start time of day/week/month/year
	# ----------------------------------------------------------------
	@staticmethod
	def timeOfDayStart(tv=None):
		"""
		获取指定时间当天的凌晨时间
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return _time.mktime((local.tm_year, local.tm_mon, local.tm_mday, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfDayEnd(tv=None):
		"""
		获取指定事件当天的结束时间（23:59:59）
		"""
		return vtime.timeOfDayStart(tv) + 86399						# 86399 = 24 * 3600 - 1

	@staticmethod
	def timeOfWeekStart(tv=None):
		"""
		获取指定时间所在星期的周一凌晨时间值（周起始时间）
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		y, m, d = local.tm_year, local.tm_mon, local.tm_mday
		dayStart = _time.mktime((y, m, d, 0, 0, 0, 0, 0, 0))		# 当天的凌晨时间值
		return dayStart - local.tm_wday * 86400						# 86400 = 3600 * 24

	@staticmethod
	def timeOfWeekEnd(tv=None):
		"""
		获取指定时间所在星期的周日结束时间值（23:59:59）
		"""
		return vtime.timeOfWeekStart(tv) + 604799					# 604799 = 3600 * 24 * 7 - 1

	@staticmethod
	def timeOfMWeekthStart(tv=None):
		"""
		获取指定时间所在当月“第几个星期”的起始时间值（以周一为每个星期的第一天）
		"""
		weekth = vtime.mweekth(tv)
		if weekth > 1:								# 如果是第二个星期以上
			return vtime.timeOfWeekStart(tv)		# 则与其星期起始时间是一样的
		if tv is None: tv = fnow()					# 如果是第一个星期
		local = _time.localtime(tv)					# 则返回的是一号的凌晨时间
		return _time.mktime((local.tm_year, local.tm_mon, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfMWeekthEnd(tv=None):
		"""
		获取指定时间所在当月“第几个星期”的结束时间值（23:59:59）
		"""
		if tv is None: tv = fnow()
		weekth = vtime.mweekth(tv)					# 指定时间在第几个星期
		local = _time.localtime(tv)
		year, mon = local.tm_year, local.tm_mon
		weeks = vdate.weeksOfMon(year, mon)			# 指定时间所在月份一共有几个星期
		if weekth >= weeks:							# 指定时间在当月最后一个星期
			lastDay = vdate.daysOfMon(year, mon)	# 指定时间所在月最后一天是几号
			return _time.mktime((year, mon, lastDay, 23, 59, 59, 0, 0, 0))		# 最后一天的结束时间
		return vweek.timeOfMWeekthStart(year, mon, weekth+1) - 1				# 下一个星期的起始时间减去一秒

	@staticmethod
	def timeOfYWeekthStart(tv=None):
		"""
		获取指定时间所在年“第几个星期”的起始时间值（以周一为每个星期的第一天）
		"""
		weekth = vtime.yweekth(tv)
		if weekth > 1:
			return vtime.timeOfWeekStart(tv)
		if tv is None: tv = fnow()					# 如果是年第一个星期
		local = _time.localtime(tv)					# 则返回的是一月一号的凌晨时间
		return _time.mktime((local.tm_year, 1, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfYWeekthEnd(tv=None):
		"""
		获取指定时间所在年“第几个星期”的结束时间值（23:59:59）（以周日为每个星期的最后一天）
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		y, m, d = local.tm_year, local.tm_mon, local.tm_mday
		weeks = vdate.weeksOfYear(y)				# 指定时间所在年份一共有（跨）多少个星期
		yweekth = vdate.yweekth(y, m, d)			# 指定时间在当年的第几个星期
		if yweekth >= weeks:						# 如果是在最后一个星期，则返回年最后一天的结束时间
			return _time.mktime((y, 12, 31, 23, 59, 59, 0, 0, 0))
		return vweek.timeOfYWeekthStart(y, yweekth+1) - 1	# 否则返回下一个星期的起始时间减一

	@staticmethod
	def timeOfMonthStart(tv=None):
		"""
		获取指定时间所在月份的一号凌晨时间值（月起始时间）
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return _time.mktime((local.tm_year, local.tm_mon, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfMonthEnd(tv=None):
		"""
		获取指定时间所在月份的最后一天的结束时间（23:59:59）
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		year, mon = local.tm_year, local.tm_mon
		lastDay = vdate.daysOfMon(year, mon)								# 指定时间所在月一共有多少天
		return _time.mktime((year, mon, lastDay, 23, 59, 59, 0, 0, 0))		# 最后一天的结束时间

	@staticmethod
	def timeOfYearStart(tv=None):
		"""
		获取指定时间值所在年份的一月一号的时间值
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return _time.mktime((local.tm_year, 1, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfYearEnd(tv=None):
		"""
		获取指定时间值所在年份的最后一天的结束时间（23:59:59）
		"""
		if tv is None: tv = fnow()
		local = _time.localtime(tv)
		return _time.mktime((local.tm_year, 12, 31, 23, 59, 59, 0, 0, 0))


# --------------------------------------------------------------------
# 输入日期的日程换算
# --------------------------------------------------------------------
class vdate:
	@staticmethod
	def isLeapYear(year):
		"""
		判断指定年是否是闰年（闰年 2 月份有 29 天）：
			可被 400 整除，或可被 4 整除同时不被 100 整除
		"""
		if year % 400 == 0: return True
		if year % 4 != 0: return False
		if year % 100 == 0: return False
		return True

	@staticmethod
	def daysOfMon(year, mon):
		"""
		获取指定月份的天数
		"""
		if mon < 1 or mon > 12:
			raise ValueError("month must between 1 ~ 12.")
		if mon == 2:
			return 29 if vdate.isLeapYear(year) else 28
		if mon < 8:
			return 30 + mon % 2
		return 31 - mon % 2

	@staticmethod
	def daysOfYear(year):
		"""
		获取指定年份的天数
		"""
		return 356 if vdate.isLeapYear(year) else 365

	@staticmethod
	def weeksOfMon(year, mon):
		"""
		指定月份有几个星期
		"""
		days = vdate.daysOfMon(year, mon)			# 当月天数
		startWDay = vdate.wday(year, mon, 1)		# 当月一号是星期几
		firstWeekDays = 8 - startWDay				# 第一个星期占用的天数
		days = days - firstWeekDays
		return int(math.ceil(days /  7.0)) + 1

	@staticmethod
	def weeksOfYear(year):
		"""
		指定年份一共有几个星期（跨几个星期）
		"""
		days = vdate.daysOfYear(year)				# 指定年份的总天数
		startWDay = vdate.wday(year, 1, 1)			# 一月一号为星期几
		firstWeekDays = 8 - startWDay				# 第一个星期占用的天数
		days = days - firstWeekDays					# 除去第一个星期占用天数后剩余天数
		return int(math.ceil(days / 7.0)) + 1


	# ----------------------------------------------------------------
	# day in week/year
	# ----------------------------------------------------------------
	@staticmethod
	def wday(y, m, d):
		"""
		获取指定日期所在星期
		"""
		return datetime.datetime(y, m, d).weekday() + 1

	@staticmethod
	def yday(y, m, d):
		"""
		获取指定日期所在当年的第几天
		"""
		return datetime.datetime(y, m, d).timetuple().tm_yday


	# ----------------------------------------------------------------
	# week in month/year
	# ----------------------------------------------------------------
	@staticmethod
	def mweekth(y, m, d):
		"""
		获取指定日期是当月的第几个星期（顺序为：一、二、三、四、五、六、日。即星期的起始日为周一）
		"""
		dayIndex = d - 1											# 一号索引
		weekDayIndex_1 = datetime.datetime(y, m, 1).weekday()		# 一号的星期索引
		return (dayIndex + weekDayIndex_1) / 7 + 1

	@staticmethod
	def yweekth(y, m, d):
		"""
		获取指定日期是当年的第几个星期
		"""
		dayTime = _time.mktime((y, m, d, 0, 0, 0, 0, 0, 0))
		yday = _time.localtime(dayTime).tm_yday
		ydayIndex = yday - 1										# 一年的第几天的索引
		weekDayIndex_11 = datetime.datetime(y, 1, 1).weekday()		# 一月一号的星期索引
		return (ydayIndex + (weekDayIndex_11 % 6)) / 7 + 1


	# ----------------------------------------------------------------
	# start time of day/week/month/year
	# ----------------------------------------------------------------
	@staticmethod
	def timeOfDayStart(y, m, d):
		"""
		获取指定日期当天的凌晨时间
		"""
		return _time.mktime((y, m, d, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfDayEnd(y, m, d):
		"""
		获取指定日期的当天结束时间（23:59:59）
		"""
		return _time.mktime((y, m, d, 23, 59, 59, 0, 0, 0))

	@staticmethod
	def timeOfWeekStart(y, m, d):
		"""
		获取指定日期所在星期的周一凌晨时间值（周起始时间）
		"""
		dayStart = _time.mktime((y, m, d, 0, 0, 0, 0, 0, 0))	# 指定日期凌晨时间值
		local = _time.localtime(dayStart)
		return dayStart - local.tm_wday * 86400					# 8640 = 24 * 3600

	@staticmethod
	def timeOfWeekEnd(y, m, d):
		"""
		获取指定日期所在星期的周末（周日）结束时间值（23:59:59）
		"""
		return vdate.timeOfWeekStart(y, m, d) + 604800 - 1		# 604800 = 24 * 3600 * 7

	@staticmethod
	def timeOfMWeekthStart(y, m, d):
		"""
		获取指定日期所在当月“第几个星期”的起始时间值（以周一为每个星期的第一天）
		"""
		weekth = vdate.mweekth(y, m, d)
		if weekth > 1: return vdate.timeOfWeekStart(y, m, d)
		return _time.mktime((y, m, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfMWeekthEnd(y, m, d):
		"""
		获取指定日期所在当月“第几个星期”的结束时间值（23:59:59）（以周日为每个星期的最后一天）
		"""
		weekth = vdate.mweekth(y, m, d)					# 指定日期在当月第几个星期
		weeks = vdate.weeksOfMon(y, m)					# 指定日期所在月跨几个星期
		if weekth >= weeks:								# 指定日期在最后一个星期
			lastDay = vdate.daysOfMon(y, m)				# 指定日期所在月最后一天
			return _time.mktime((y, m, lastDay, 23, 59, 59, 0, 0, 0))
		return vweek.timeOfMWeekthStart(y, m, weekth+1) - 1						# 下一个星期的起始时间减去一秒

	@staticmethod
	def timeOfYWeekthStart(y, m, d):
		"""
		获取指定日期所在年“第几个星期”的起始时间值（以周一为每个星期的第一天）
		"""
		weekth = vdate.yweekth(y, m, d)
		if weekth > 1: return vdate.timeOfWeekStart(y, m, d)
		return _time.mktime((y, 1, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfYWeekthEnd(y, m, d):
		"""
		获取指定日期所在年“第几个星期”的结束时间值（23:59:59）（以周日为每个星期的最后一天）
		"""
		weeks = vdate.weeksOfYear(y)				# 指定时间所在年份一共有（跨）多少个星期
		yweekth = vdate.yweekth(y, m, d)			# 指定时间在当年的第几个星期
		if yweekth >= weeks:						# 如果是在最后一个星期，则返回年最后一天的结束时间
			return _time.mktime((y, 12, 31, 23, 59, 59, 0, 0, 0))
		return vweek.timeOfYWeekthStart(y, yweekth+1) - 1	# 否则返回下一个星期的起始时间减一

	@staticmethod
	def timeOfMonthStart(y, m):
		"""
		获取指定年月的一号凌晨时间值（月起始时间）
		"""
		return _time.mktime((y, m, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfMonthEnd(y, m):
		"""
		获取指定年月的最后一天结束时间值（23:59:59）
		"""
		mdays = vdate.daysOfMon(y, m)
		return _time.mktime((y, m, mdays, 23, 59, 59, 0, 0, 0))

	@staticmethod
	def timeOfYearStart(year):
		"""
		获取指定年份的一月一号的时间值
		"""
		return _time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfYearEnd(year):
		"""
		获取指定年份的最后一天的时间值（23:59:59）
		"""
		return _time.mktime((year, 12, 31, 23, 59, 59, 0, 0, 0)) - 1


# --------------------------------------------------------------------
# 输入星期的日程换算
# --------------------------------------------------------------------
class vweek:
	@staticmethod
	def timeOfMWeekthStart(year, mon, weekth):
		"""
		获取指定年月的第 weekth 个星期的起始时间（星期的首日为周一）
		"""
		time1 = _time.mktime((year,  mon, 1, 0, 0, 0, 0, 0, 0))
		if weekth <= 1: return time1								# 首个星期返回一号的时间
		local = _time.localtime(time1)
		day = (weekth - 1) * 7 + 1 - local.tm_wday					# 指定第 weekth 个星期起始日的号数
		day = min(day, vdate.daysOfMon(year, mon))					# 当月最多几天
		return _time.mktime((year,  mon, day, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfMWeekthEnd(year, mon, weekth):
		"""
		获取指定年份第 weekth 个星期的结束时间值（23:59:59）（星期的最后一天为周日）
		"""
		weeks = vdate.weeksOfMon(year, mon)							# 指定年月有（跨）几个星期
		if weekth >= weeks:											# 如果是最后一个星期，则返回指定月份最后一天的结束时间
			mdays = vdate.daysOfMon(year, mon)						# 指定年月总天数
			return _time.mktime((year, mon, mdays, 23, 59, 59, 0, 0, 0))
		return vweek.timeOfMWeekthStart(weekth+1) - 1				# 否则返回下一个星期的起始时间减一

	@staticmethod
	def timeOfYWeekthStart(year, weekth):
		"""
		获取指定年份的第 weekth 个星期的起始时间
		"""
		time11 = _time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))
		if weekth <= 1: return time11								# 首个星期返回一月一号的时间
		local = _time.localtime(time11)
		day = (weekth - 1) * 7 + 1 - local.tm_wday					# 指定第 weekth 个星期为当年的第几天
		maxDays = vdate.daysOfYear(year)
		mon = 1
		while mon <= 12:
			mdays = vdate.daysOfMon(year, mon)
			if day <= mdays: break
			day = day - mdays
			mon += 1
		return _time.mktime((year,  mon, day, 0, 0, 0, 0, 0, 0))

	@staticmethod
	def timeOfYWeekthEnd(year, weekth):
		"""
		获取指定年份的第 weekth 个星期的结束时间（23:59:59）
		"""
		weeks = vdate.weeksOfYear(year)
		if weekth >= weeks:
			return _time.mktime((year, 12, 31, 23, 59, 59, 0, 0, 0))
		return vweek.timeOfYWeekthStart(year, weekth+1) - 1
