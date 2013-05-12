Getting started
======

1. Install Python 2.6 or higher (but not Python 3.x). On Windows, make sure to install the 32-bit version (x86).
2. Install the python **mysqldb** library using your favourite package manager. On Windows, use [this installer](https://pypi.python.org/packages/2.7/M/MySQL-python/MySQL-python-1.2.4.win32-py2.7.exe#md5=313b4ceed0144a3019f87a4fba5168d6).
3. If you're using Windows, install the [python curses library](http://www.lfd.uci.edu/~gohlke/pythonlibs/6i2y2ngm/curses-2.2.win32-py2.7.exe).
4. Clone the Uforia repository using git (`git clone https://github.com/uforia/Uforia.git`)
5. Inside the `source/include` diectory copy the `config.py.example` file and rename it to `config.py`. You should probably modify the `STARTDIR` and database configuration values.
6. Run uforia.py (multiprocessing version) or uforia_debug.py (single process, supports breakpoints)

*(The installation instructions will be extended soon)*
