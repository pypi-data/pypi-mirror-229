# Aquarius Time: Scientific time library for Python

Aquarius Time is a Python library for performing time calculations which aims
to be more convenient for scientific applications than the default Python time
library (datetime). It uses the standard of Julian date, i.e. the fractional
number of days from -4712-01-01 12:00 as the basis for time representation, and
allows conversion between Python datetime, date arrays and ISO 8601 time.

## Installation

Installation on Linux is recommended.

### Linux

1. Install the required system packages. On Debian-derived distributions
   (Ubuntu, Devuan, ...):

   ```
   apt install python3-full python3-pip python3-venv pipx
   ```

   On Fedora:

   ```
   sudo yum install python3 python3-pip pipx
   ```

2. Install Aquarius Time. If you indend to use the Python interface, you can
   install in the home directory with pip3:

   ```
   pip3 install aquarius-time
   ```

   Replace pip3 with pip if pip3 is not available. Add `--break-system-packages`
   if your distribution does not allow installing into the home directory but
   you want to anyway.

   Alternatively, install into a Python virtual environment with:

   ```
   python3 -m venv venv
   . venv/bin/activate
   pip3 install aquarius-time
   ```

   You can then use the Aquarius Time Python interface from within the virtual
   environment. Deactivate the environment with `deactivate`.

   If you only indend to use the command-line interface,
   you can install Aquarius Time with pipx:

   ```
   pipx install aquarius-time
   ```

   You might have to add `$HOME/.local/bin` to the PATH environment variable
   if not present already in order to access the aq command. This can be done
   with `pipx ensurepath`.

You should now be able to run the command `aq`.

### Windows

1. Install [Python](https://www.python.org/). In the installer, tick `Add
python.exe to PATH`.

2. Open the Command Prompt from the Start menu. Install Aquarius Time with:

    ```
	pip3 install aquarius-time
	```

You should now be able to run the command `aq`.

### macOS

Open the Terminal. Install Aquarius Time with:

```
python3 -m pip install aquarius-time
```

Make sure that `/Users/<user>/Library/Python/<version>/bin` is included in the
`PATH` environment variable if not already, where `<user>` is your system
user name and `<version>` is the Python version. This path should be printed
by the above command. This can be done by adding this line to the file
`.zprofile` in your home directory and restart the Terminal:

```
PATH="$PATH:/Users/<user>/Library/Python/<version>/bin"
```

You should now be able to run the command `aq`.

## Uninstallation

To uninstall if installed with pipx:

```
pipx uninstall aquarius-time
```

To uninstall if installed with pip3 or pip:

```
pip3 uninstall aquarius-time
```

Replace pip3 with pip if pip3 is not available.

## Python interface

```python
import aquarius_time as aq
```

In the description below, an "array" means an instance of `list`, `tuple` or
`numpy.ndarray`.

### from_datetime

```python
aq.from_datetime(x)
```

Convert Python datetime `x` to Julian date.

- `x`: `datetime` instance or an array of `datetime` instances.

Returns a Julian date (`float`) or an array of Julian dates (type
`numpy.float64` if `x` is an instance of `numpy.ndarray` or `float` otherwise)
if `x` is an array.

### to_datetime

```python
aq.to_datetime(x)
```

Convert Julian date `x` to Python datetime.

- `x`: Julian date (`float`) or an array of Julian dates (type `numpy.float64`
if `numpy.ndarray` or `float` otherwise).

Returns `datetime` or an array of `datetime` if `x` is an array.

### from_iso

```python
aq.from_iso(x)
```

Convert ISO 8601 time to Julian date.

- `x`: ISO 8601 time (`str`) or an array of ISO 8601 times.

Returns a Julian date (`float`) or an array of Julian dates (type
`numpy.float64` if `x` is an instance of `numpy.ndarray` or `float` otherwise)
if `x` is an array.

### to_iso

```python
aq.to_iso(x)
```

Convert Julian date to ISO 8601 time.

- `x`: Julian date (`float) or an array of Julian dates (type `numpy.float64`
  if `np.ndarray` or `float` otherwise).

Returns ISO 8601 time (`str`) of an array of ISO 8601 times (type `str`) if `x`
is an array.

### from_date

```python
aq.from_date(x)
```

Convert date (see [Date](#date)) to Julian date.

- `x`: Date (see [Date](#date)),

Returns a Julian date (`float`) or an array of Julian dates (type
`numpy.float64` if `x` is an instance of `numpy.ndarray` or `float` otherwise)
if `x` is an array.

### to_date

```python
aq.to_date(x)
```

Convert Julian date to date (see [Date](#date)).

- `x`: Julian date (`float`) or an array of Julian dates (type `numpy.float64`
if `numpy.ndarray` or `float` otherwise).

Returns date (see [Date](#date)).

## Date

Date is a `list` containing numbers or instances of `numpy.ndarray` in the
following order:

0. Calendar (see Calendar below) (int8).
1. Year (int32).
2. Month (int8).
3. Day (int8).
4. Hour (int8).
5. Minute (int8).
6. Second (int8).
7. Fraction of a second (float64).

Calendar:

- `1`: Gregorian calendar.

## Command line interface

### aq

Synopsis:

`aq` *from* *to* [*value*...]

Convert value(s) from one time format to another. The converted value(s) is
printed to the standard output. If no values are provided as command line
arguments, read values from the standard input, separated by new lines. If a
value cannot be converted, print `none`.

Arguments:

- *from*: From format (see Format below).
- *to*: To format (see Format below).
- *value*: Value to be converted.

Format:

- `jd`: Julian date.
- `iso`: ISO 8601.

## License

MIT. See [LICENSE.md](LICENSE.md).

## Releases

### 0.3.0 (2023-09-08)

- Support for lists, tuples, masked and multi-dim arrays, while preserving the
  variable type.
- Fixed installation on Windows.
- Improved documentation.

### 0.2.0 (2023-03-24)

- Fixed handling of fractions of a second in from\_date.
- Discontinued support for Python 2.

### 0.1.0 (2020-04-29)

- Initial development release.
