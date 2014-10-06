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

# Parses the IE cookies format (IE5 - IE10)

# TABLE: cookies:LONGTEXT

import sys
import traceback
import os
import re
import datetime

def _timestamp_from_cookie(low, high):
    """
    Convert time from the cookie (Win32 time format, in high and low
    order parts) to a UNIX timestamp. Verified with the IECookiesView
    tool.
    """
    return int(1e-7 * (high * pow(2, 32) + low) - 11644473600)


def _parse_cookies(filename):
    """
    Return a dict with the parsed IE cookies from the specified file.
    If the file does not contain cookies, None is returned.
    filename - The path to the file
    """
    # Maximum number of bytes to read for giving up checking for cookie.
    # Note that the maximum size of a cookie is 4096 bytes (excluding
    # key names, timestamps, etc)
    HARD_LIMIT = 7000

    # The states for parsing the cookies
    RESET_STATE = 0
    KEY_STATE = 1
    VALUE_STATE = 2
    DOMAIN_STATE = 3
    FLAGS_STATE = 4 # Cookie bitflags
    EXPIRE_LO_STATE = 5 # Expiry low-order bytes
    EXPIRE_HI_STATE = 6 # Expiry high-order bytes
    CREATION_LO_STATE = 7 # Creation date low-order bytes
    CREATION_HI_STATE = 8 # Creation date high-order bytes
    DELIMITER_STATE = 9

    state = KEY_STATE

    cookies = []
    # Temporary store for cookie data (conversion to the correct data
    # type will happen later.)
    buf = {}

    # Reset after each delimiter. Should not exceed HARD_LIMIT
    counter = 0

    file = open(filename, "rb")
    try:
        while True:
            # Read 1 byte
            b = file.read(1)

            counter += 1
            if counter > HARD_LIMIT:
                # Give up.
                return None
            if b == "":
                # EOF
                break

            # Fills the buffer for each state until the last
            if state < DELIMITER_STATE:
                if b == '\n':
                    state += 1
                else:
                    if state in buf:
                        buf[state] += b
                    else:
                        buf[state] = b
            else:
                # Convert cookie data
                cookie = {}
                cookie["key"] = buf[KEY_STATE]
                cookie["value"] = buf[VALUE_STATE]
                cookie["domain"] = buf[DOMAIN_STATE]
                cookie["flags"] = int(buf[FLAGS_STATE])
                cookie["expire"] = datetime.fromtimestamp(_timestamp_from_cookie( \
                    int(buf[EXPIRE_LO_STATE]), int(buf[EXPIRE_HI_STATE]))).isoformat()
                cookie["creation"] = datetime.fromtimestamp(_timestamp_from_cookie( \
                    int(buf[CREATION_LO_STATE]), int(buf[CREATION_HI_STATE]))).isoformat()
                cookies.append(cookie)

                # Reset everything
                buf = {}
                state = RESET_STATE
                counter = 0

    except:
        # Parsing problem (to be expected with non-cookie files), don't
        # warn, return nothing.
        return None
    finally:
        file.close()

        # Rationale: if no cookies were stored/found, then it is not
        # a cookie file; so return None instead of an empty list.
        return cookies if len(cookies) > 0 else None


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    try:
        # Check the name of our file, if it matches the old cookie name
        # pattern (user@domain[<nr>].txt) or the new obfuscated one
        # (eight random characters) in IE9+, continue; otherwise stop.
        filename = os.path.basename(fullpath)
        if not re.search(r".*@.*\[[0-9]+\]\.txt", filename) \
        and not re.search(r"([A-Z0-9]){6}\.txt", filename):
            return None

        cookies = _parse_cookies(fullpath)
        if cookies == None:
            # Was not a (valid) cookie file, so don't store it.
            return None

        # Print the cookies if DEBUG is True
        if config.DEBUG:
            print "\nInternet Explorer cookie file data:"
            print "%-18s %s" % (columns[0], cookies)
            print

        return [cookies]
    except:
        traceback.print_exc(file=sys.stderr)

        return None
