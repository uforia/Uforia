Getting started
======

Linux
-----
Make sure your distribution provides **Python 2.7**+ (Python 2.6 works, but future compatibility is not guaranteed). Currently there is only one data storage format which requires **MySQL** (or any drop-in replacement such as MariaDB) and the python **mysqldb** package.
```
# apt-get install python2.7
# apt-get install mysql-server mysql-client python-mysqldb
```

A new database will need to be created. You can do this using the command line. Example:
```
# mysql -uroot -p
mysql> CREATE DATABASE uforia;
mysql> GRANT USAGE ON *.* to uforia@localhost IDENTIFIED BY ‘uforia’;
mysql> GRANT ALL PRIVILEGES ON uforia.* to uforia@localhost ;
```

Windows
-------
Make sure to install the 32-bit version of Python 2.7, as the currently included Windows libraries haven't been built with a 64-bit **GCC** ([MinGW.org](http://mingw.org) does not yet provide a 64-bit version of its runtime). You will also need the curses and mysqldb python libraries.

##### Download links
* [Python 2.7 x86](http://www.python.org/ftp/python/2.7.4/python-2.7.4.msi) <br>
* [Curses for python](http://www.lfd.uci.edu/~gohlke/pythonlibs/6i2y2ngm/curses-2.2.win32-py2.7.exe) <br>
* [Mysqldb library for python](https://pypi.python.org/packages/2.7/M/MySQL-python/MySQL-python-1.2.4.win32-py2.7.exe#md5=313b4ceed0144a3019f87a4fba5168d6)

There are many options for the installation of a MySQL server on Windows. You can use e.g. [XAMPP](http://www.apachefriends.org/en/xampp.html), [Oracle's installer](http://dev.mysql.com/downloads/mysql/), or [MariaDB](https://downloads.mariadb.org/mariadb/5.5.30/).

If using **MariaDB**, you can create a new database using the included **HeidiSQL** GUI client. Similarly, **XAMPP** users can use **PHPMyAdmin**.

Configuration
-------------
After satisfying all prerequisites, we will still need to supply a configuration file to Uforia. It is recommended to copy the `config.py.example` file inside `source/include` and renaming it to `config.py`. See the descriptions in `config.py.example` for which settings need to be changed. It is probably necessary to change `STARTDIR, DBHOST, DBNAME, DBUSER` and `DBPASS`.

Running Uforia
--------------
There are two python programs provided in the source directory; `uforia.py` and `uforia_debug.py`. While the output of both programs should be the same, the former uses multiprocessing (for production, better performance), and the latter uses a single process (which is useful for debugging). You can execute them directly from the command line or double clicking (Windows). Depending on your configuration you should see a lot of text pass by, or you should simple see 'Uforia starting...' and 'Uforia completed...' when DEBUG mode is off.

Additional notes
----------------
For full-text search support, Uforia stores the contents of all plain-text files in its database. This might cause problems with certain database configurations. For MySQL, it is recommended to increase the value of the maximum allowed packet size: http://dev.mysql.com/doc/refman/4.1/en/packet-too-large.html
