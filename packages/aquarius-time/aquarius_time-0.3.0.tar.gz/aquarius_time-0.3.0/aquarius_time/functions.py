import datetime as dt
import numpy as np

def parse_iso(s):
	formats = [
		'%Y-%m-%dT%H:%M:%SZ',
		'%Y-%m-%dT%H:%M:%S',
		'%Y-%m-%dT%H:%M',
		'%Y-%m-%d',
	]
	for f in formats:
		try: return dt.datetime.strptime(s, f)
		except: pass
	return None

def for_array(func):
	def f(x):
		if isinstance(x, np.ndarray):
			shape = x.shape
			res = [func(y) for y in x.flatten()]
		elif isinstance(x, (list, tuple)):
			res = [func(y) for y in x]
		elif x is np.ma.masked:
			res = x
		else:
			res = func(x)
		if isinstance(x, np.ma.core.MaskedArray):
			return np.ma.array(res, mask=x.mask).reshape(shape)
		if isinstance(x, np.ndarray):
			return np.array(res).reshape(shape)
		if isinstance(x, tuple):
			return tuple(res)
		else:
			return res
	return f

@for_array
def from_iso(x):
	if x is np.ma.masked: return np.nan
	time_dt = parse_iso(x)
	if time_dt is None: return None
	return (time_dt - dt.datetime(1970,1,1)).total_seconds()/(24.0*60.0*60.0) + 2440587.5

@for_array
def to_iso(x):
	if x is np.ma.masked: return ''
	y = to_datetime(x)
	f = y.microsecond/1e6
	y += dt.timedelta(seconds=(-f if f < 0.5 else 1-f))
	return y.strftime('%Y-%m-%dT%H:%M:%S')

def to_date(x):
	try:
		n = len(x)
	except:
		return to_date(np.array([x]))
	cal = np.ones(n, dtype=np.int8)
	year = np.zeros(n, dtype=np.int32)
	month = np.zeros(n, dtype=np.int8)
	day = np.zeros(n, dtype=np.int8)
	hour = np.zeros(n, dtype=np.int8)
	minute = np.zeros(n, dtype=np.int8)
	second = np.zeros(n, dtype=np.int8)
	frac = np.zeros(n, dtype=np.float64)
	for i in range(n):
		y = dt.datetime(1970,1,1) + dt.timedelta(days=(x[i] - 2440587.5))
		cal[i] = 1
		year[i] = y.year
		month[i] = y.month
		day[i] = y.day
		hour[i] = y.hour
		minute[i] = y.minute
		second[i] = y.second
		frac[i] = y.microsecond*1e-6
	return [cal, year, month, day, hour, minute, second, frac]

def from_date(x):
	if x is np.ma.masked: return np.nan
	try:
		n = len(x[0])
	except:
		def get(a, i, b):
			return a[i] if len(a) > i else b
		return (dt.datetime(
			x[1],
			get(x, 2, 1),
			get(x, 3, 1),
			get(x, 4, 0),
			get(x, 5, 0),
			get(x, 6, 0),
			int(get(x, 7, 0)*1e6)
		) - dt.datetime(1970,1,1)).total_seconds()/(24.0*60.0*60.0) + 2440587.5
	y = np.zeros(n)
	for i in range(n):
		y[i] = from_date((x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i], x[7][i]))
	return y

@for_array
def to_datetime(x):
	if x is np.ma.masked: return None
	return dt.datetime(1970,1,1) + dt.timedelta(seconds=(x - 2440587.5)*24.0*60.0*60.0)

@for_array
def from_datetime(x):
	if x is np.ma.masked: return np.nan
	return (x - dt.datetime(1970,1,1)).total_seconds()/(24.0*60.0*60.0) + 2440587.5

@for_array
def year_day(x):
	if x is np.ma.masked: return np.nan
	y = to_date(x)
	z = from_date([1, y[1], 1, 1, 0, 0, 0, 0])
	return x - z
