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

# TABLE: cookies:LONGTEXT, version:INT, last_compatible_version:INT

import sys
import traceback
import mailbox
import os
import pysqlite2
import pysqlite2.dbapi2


def process(fullpath, config, rcontext, columns=None):
    try:
        # Check the name of our file, if Cookies assume Google Chrome/
        # Chromium cookies database
        if not os.path.basename(fullpath) == "Cookies":
            return None

        assorted = []
        cookies = []

        # Make db connection, cursor, and fetch all cookies.

        conn = pysqlite2.dbapi2.connect(fullpath)
        cursor = conn.cursor()

        # Get the name of the columns of cookies table and put them in
        # tablecols
        tablecols = []
        cursor.execute("PRAGMA table_info('cookies');")
        while True:
            res = cursor.fetchone()
            if res == None:
                break
            else:
                tablecols.append(res[1])

        # Get the individual cookies
        cursor.execute("SELECT * FROM cookies;")
        while True:
            res = cursor.fetchone()
            if res == None:
                break
            else:
                # Make a dict of the result and column names
                cookie = dict(zip(tablecols, res))
                cookies.append(cookie)

        assorted.append(cookies)

        # Get the version and last_compatible_version metadata
        cursor.execute("SELECT value FROM meta WHERE key = 'version'")
        assorted.append(cursor.fetchone()[0])
        cursor.execute(
            "SELECT value FROM meta "
            "WHERE key = 'last_compatible_version'")
        assorted.append(cursor.fetchone()[0])

        conn.close()

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        # Print some data that is stored in
        # the database if debug is true
        if config.DEBUG:
            print "\nGoogle Chrome cookie file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted
    except:
        traceback.print_exc(file=sys.stderr)

        return None
