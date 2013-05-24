# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Stores the 7z file metadata and starts Uforia recursively on the
# files inside the 7z folder.

# TABLE: file_names:LONGTEXT, total_files:INT, solid:INT, version:LONGTEXT, contentInfo:LONGTEXT

import sys
import traceback
import tempfile
import shutil
import os
import subprocess
from pylzmalib import py7zlib
import recursive


def _extractall(fullpath, tempdir, seven_zip_tool):
    command = ""

    #tool path
    if seven_zip_tool is not None:
        command += seven_zip_tool + " x "
    else:
        raise Exception("7zip tool not given")

    # archive path
    if fullpath is not None:
        command += fullpath + " "
    else:
        raise Exception("Archive path not given")

    # destination path
    if tempdir is None:
        raise Exception("Tempdir not given")

    # call extract command
    try:
        p = subprocess.Popen(command, cwd=tempdir)
        output = p.communicate()[0]

        # if error is given by command
        if output is not None:
            raise Exception(output)

    except Exception as e:
        raise Exception(str(e) + "    Command failed with following " +
                        "arguments: " + fullpath + " " + tempdir + " " +
                        seven_zip_tool)


def process(fullpath, config, rcontext, columns=None):
    # Try to parse 7z data
    try:
        seven_zip = py7zlib.Archive7z(open(fullpath, 'rb'))
        assorted = [seven_zip.getnames(), seven_zip.numfiles,
                 seven_zip.solid, seven_zip.version]

        # Get .7zip's content metadata and store it in an dictionary.
        # In the dictionary the key is the file name and
        # the value is an other dict with its info.
        content_info = {}
        for member in seven_zip.getmembers():
            content = {}
            content["is_emptystream"] = member.emptystream
            content["has_crc"] = member.checkcrc()
            content["digest"] = member.digest
            content["attributes"] = member.attributes
            content["compressed_size"] = member.compressed
            content["uncompressed_size"] = member.uncompressed

            content_info[member.filename] = content

        # Store content info in DB.
        assorted.append(content_info)
        del content_info

        # Try to extract the content of the rar file.
        try:
            # Create a temporary directory
            tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

            # Extract the 7zip file
            _extractall(fullpath, tmpdir, config.SEVENZIP_TOOL)

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
            print "\n7z file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i] + ':', assorted[i])

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)

        # Store values in database so not the whole application crashes
        return None
