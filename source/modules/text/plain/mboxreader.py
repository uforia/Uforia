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

# Parses the mbox mailbox format

# TABLE: messages:LONGTEXT

import sys
import traceback
import mailbox


def process(fullpath, config, rcontext, columns=None):
    try:
        with open(fullpath, "rb") as file:
            # Read the beginning of the file to check if it looks like
            # an mbox file. If not, stop.
            if not file.read(5).startswith("From "):
                return None

        messages = []
        mbox = mailbox.mbox(fullpath, create=False)
        for mboxmessage in mbox:
            message = {}
            message['flags'] = mboxmessage.get_flags()
            # Stores each line such as To:, Subject:, etc. (if present)
            for key, value in mboxmessage.items():
                message[key] = value
            messages.append(message)

        # Print some data that is stored in
        # the database if debug is true
        if config.DEBUG:
            print "\nMbox file data:"
            print "%-18s %s" % (columns[0], messages)
            print

        return [messages]
    except:
        traceback.print_exc(file=sys.stderr)
