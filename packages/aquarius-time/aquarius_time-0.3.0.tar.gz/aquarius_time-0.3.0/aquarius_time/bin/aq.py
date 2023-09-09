#!/usr/bin/env python
'''Convert from one time format to another.

Usage: aq FROM TO [VALUE...]

The converted value(s) is printed to the standard output. If no values are
provided as command line arguments, read values from the standard input,
separated by new lines. If a value cannot be converted, print "none".

Arguments:

  FROM   From format (see Format below).
  TO     To format (see Format below).
  VALUE  Value to be converted.

Format:

    jd   Julian date.
    iso  ISO 8601.
'''

import sys
import pst
import aquarius_time as aq

def noop(x): return x

FROM = {
	'iso': aq.from_iso,
	'jd': noop,
}

TO = {
	'iso': aq.to_iso,
	'jd': noop,
}

def main():
	args, opts = pst.decode_argv(sys.argv, as_unicode=True)
	if len(args) < 3:
		sys.stderr.write(sys.modules[__name__].__doc__)
		sys.exit(1)
	from_ = args[1]
	to = args[2]
	values = args[3:]

	f1 = FROM.get(from_)
	f2 = TO.get(to)

	if len(values) > 0:
		for value in values:
			x = f2(f1(value))
			print(x if x is not None else 'none')
	else:
		for value in sys.stdin.buffer.readlines():
			value = value.strip()
			try: value = float(value)
			except ValueError: pass
			x = f2(f1(value))
			print(x if x is not None else 'none')

if __name__ == '__main__':
	main()
