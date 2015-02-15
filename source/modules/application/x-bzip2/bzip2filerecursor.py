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

# Module for extracting .bz2 files and running uforia over the extracted
# file

# TABLE: Dummy:INT

import sys
import traceback
import tempfile
import shutil
import bz2
import os
import recursive


def _uncompressed_filename(fullpath):
    """
    Returns the filename for the unbzipped file. Examples:
    test.txt.bz2 => test.txt
    test.tbz => test.tar
    test => test~unbzipped
    """
    lastpart = os.path.relpath(fullpath, os.path.dirname(fullpath))
    if lastpart.endswith(".bz2"):
        return lastpart[:-3]
    elif lastpart.endswith(".tbz"):
        return lastpart[:-4] + ".tar"
    else:
        return lastpart + "~unbzipped"


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    try:
         # Create a temporary directory
        tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

        # Open bzip2 file for reading
        file = bz2.BZ2File(fullpath, 'rb')

        # Read the uncompressed data
        file_content = file.read()

        # Write it to the temp folder
        uncompressed_file = open(tmpdir + os.path.sep
                                 + _uncompressed_filename(fullpath),
                                 "wb")

        uncompressed_file.write(file_content)

        # Close both files
        uncompressed_file.close()
        file.close()

        # Call Uforia recursively
        recursive.call_uforia_recursive(config, rcontext, tmpdir,
                                        os.path.dirname(fullpath))

        # Delete the temporary directory, proceed even if it causes
        # an error
        try:
            shutil.rmtree(tmpdir)
        except:
            traceback.print_exc(file=sys.stderr)

        return None
    except:
        traceback.print_exc(file=sys.stderr)
    return None
