# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Module for extracting .gz files and running uforia over the extracted
# file

# TABLE: extrabuf:LONGTEXT, extrasize:INT, extrastart:INT

import sys
import traceback
import tempfile
import shutil
import gzip
import os
import recursive


def _uncompressed_filename(fullpath):
    """
    Returns the filename for the ungzipped file. Examples:
    test.txt.gz => test.txt
    test.tgz => test.tar
    test => test~ungzipped
    """
    lastpart = os.path.relpath(fullpath, os.path.dirname(fullpath))
    if lastpart.endswith(".gz"):
        return lastpart[:-3]
    elif lastpart.endswith(".tgz"):
        return lastpart[:-4] + ".tar"
    else:
        return lastpart + "~ungzipped"


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    try:
         # Create a temporary directory
        tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

        # Open gzip file for reading
        file = gzip.open(fullpath, 'rb')

        # Store gzip metadata values
        assorted = [file.extrabuf,
                    file.extrasize,
                    file.extrastart]

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

        return assorted
    except:
        traceback.print_exc(file=sys.stderr)
    return None
