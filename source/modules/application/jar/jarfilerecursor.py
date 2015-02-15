#!/usr/bin/env python

# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Stores the jar file metadata and starts Uforia recursively on the
# files inside the jar folder.

# TABLE: file_names:LONGTEXT, total_files:INT, zip_stored:INT, zip_deflated:INT, debug:LONGTEXT, comment:LONGTEXT, content_info:LONGTEXT

import sys
import traceback
import imp


def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath
        # Try to parse jar data
        try:
            # Get instance of zip module
            zip_module = imp.load_source('zipfilerecursor',
                                         'modules/application/' +
                                         'zip/zipfilerecursor.py')

            # JAR files works the same as ZIP files so let the ZIP module
            # handle the file.
            assorted = zip_module.process(fullpath, config, rcontext, columns)

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
