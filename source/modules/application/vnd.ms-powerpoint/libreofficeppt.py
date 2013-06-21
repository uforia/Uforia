# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the module for ppt files

# TABLE: Module_Only_Used_For_Conversion:LONGTEXT

import sys
import traceback
import tempfile
import subprocess
import shutil
import libutil
import recursive


def convert_ppt(fullpath, tempdir):
    # Try parsing ppt data
    libreoffice = libutil.get_libreoffice_executable()

    # Path that leads to the extraction tool
    if libreoffice is None:
        raise Exception("libreoffice tool not given")

    # Path that leads to the archive
    if fullpath is None:
        raise Exception("Archive path not given")

    # Path that leads to the destination
    if tempdir is None:
        raise Exception("Tempdir not given")

    # Call extract command
    try:
        # Run commands in working directory
        p = subprocess.Popen([libreoffice, "-headless", "-convert-to",
                              "jpg", fullpath], cwd=tempdir)
        output = p.communicate()[0]

        p = subprocess.Popen([libreoffice, "-headless", "-convert-to",
                              "odt", fullpath], cwd=tempdir)
        output2 = p.communicate()[0]

        p = subprocess.Popen([libreoffice, "-headless", "-convert-to",
                              "xml", fullpath], cwd=tempdir)
        output3 = p.communicate()[0]

        p = subprocess.Popen([libreoffice, "-headless", "-convert-to",
                              "txt:text", fullpath], cwd=tempdir)
        output4 = p.communicate()[0]

        # If error is given by command raise exception
        if (output is not None or output2 is not None or output3 is not None
            or output4 is not None):
            raise Exception(output, output2, output3, output4)

    except Exception as e:
        raise Exception(str(e) + "    Command failed with following " +
                        "arguments: " + fullpath + " " + tempdir + " " +
                        libreoffice)

def process(fullpath, config, rcontext, columns=None):
        # Try to parse ppt data
        try:
            assorted = ["Not_implemented"]
            
            # Try to parse the ppt file
            try:
                # Create a temporary directory
                tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

                # Parse the ptt file
                convert_ppt(fullpath, tmpdir)

                recursive.call_uforia_recursive(config, rcontext, tmpdir, fullpath)
            except:
                traceback.print_exc(file=sys.stderr)

            # Delete the temporary directory, proceed even if it causes
            # an error
            try:
                pass
                shutil.rmtree(tmpdir)
            except:
                traceback.print_exc(file=sys.stderr)

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nPPT file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i] + ':', assorted[i])

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
