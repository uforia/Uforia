# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#!/usr/bin/env python

# Read firefox cookies (cookies.sqlite)

# TABLE: cookies:LONGTEXT

import sys
import traceback
import mailbox
import os
import sqlite3


def process(fullpath, config, rcontext, columns=None):
    try:
        # Check the name of our file, if cookies.sqlite assume
        # Mozilla Firefox cookies database
        if not os.path.basename(fullpath) == "cookies.sqlite":
            return None

        cookies = []

        # Make db connection, cursor, and fetch all cookies.

        conn = sqlite3.connect(fullpath)
        cursor = conn.cursor()

        # Get the name of the columns of moz_cookies and put them in
        # tablecols
        tablecols = []
        cursor.execute("PRAGMA table_info('moz_cookies');")
        while True:
            res = cursor.fetchone()
            if res == None:
                break
            else:
                tablecols.append(res[1])

        # Get the individual cookies
        cursor.execute("SELECT * FROM moz_cookies;")
        while True:
            res = cursor.fetchone()
            if res == None:
                break
            else:
                # Make a dict of the result and column names
                cookie = dict(zip(tablecols, res))
                cookies.append(cookie)

        conn.close()

        # Print some data that is stored in
        # the database if debug is true
        if config.DEBUG:
            print "\nMozilla Firefox cookie file data:"
            print "%-18s %s" % (columns[0], cookies)
            print

        return [cookies]
    except:
        traceback.print_exc(file=sys.stderr)

        return None
