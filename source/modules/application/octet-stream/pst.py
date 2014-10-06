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

# Read MS Outlook PST/OST files (both <=2002 >=2003)

import shutil
import subprocess
import sys
import tempfile
import traceback

import libutil
import recursive


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    if file.btype.startswith("Microsoft Outlook email folder"):
        readpst_path = libutil.get_executable("libpst", "readpst")

        tempdir = None

        try:
            tempdir = tempfile.mkdtemp(dir=config.EXTRACTDIR)

            p = subprocess.Popen([
                readpst_path,
                '-e',
                '-q',
                '-o',
                tempdir,
                fullpath
            ])

            err = p.communicate()[1]

            if err is not None:
                raise Exception("readpst failed to extract " + fullpath)

            recursive.call_uforia_recursive(config, rcontext, tempdir, fullpath)
        except:
            traceback.print_exc(file=sys.stderr)
        finally:
            try:
                if tempdir:
                    shutil.rmtree(tempdir)  # delete directory
            except OSError as exc:
                traceback.print_exc(file=sys.stderr)
