# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Stores the zip file metadata and starts Uforia recursively on the
# files inside the zip folder.

# TABLE: file_names:LONGTEXT, total_files:INT, zip_stored:INT, zip_deflated:INT, debug:LONGTEXT, comment:LONGTEXT, contentInfo:LONGTEXT

import sys
import traceback
import os
import tempfile
import shutil
import copy
import zipfile
import base64
import recursive


def process(fullpath, config, rcontext, columns=None):
    try:
        # Open the zipfile
        zip = zipfile.ZipFile(fullpath, mode='r')

        # Get .zip metadata
        assorted = [zip.namelist(), len(zip.namelist()), zipfile.ZIP_STORED,
                    zipfile.ZIP_DEFLATED, zip.debug, zip.comment]

        # Get .zip's content metadata and store it in an dictionary.
        # In the dictionary the key is the file name and
        # the value is an other dict with its info.
        content_info = {}
        for info in zip.infolist():
            content = {}
            content["date_time"] = info.date_time
            content["compress_type"] = info.compress_type
            content["comment"] = info.comment
            content["create_system"] = info.create_system
            content["create_version"] = info.create_version
            content["extract_version"] = info.extract_version
            content["reserved"] = info.reserved
            content["flag_bits"] = info.flag_bits
            content["volume"] = info.volume
            content["internal_attr"] = info.internal_attr
            content["external_attr"] = info.external_attr
            content["header_offset"] = info.header_offset
            content["CRC"] = info.CRC
            content["compress_size"] = info.compress_size
            content["file_size"] = info.file_size
            content["_raw_time"] = info._raw_time

            # The extra tag needs to be encoded for JSON
            if not info.extra:
                content["extra"] = info.extra
            else:
                base64.b64encode(info.extra)

            content_info[info.filename] = content

        # Store content info in DB.
        assorted.append(content_info)
        del content_info

        # Try to extract the content of the zip file.
        try:
            # Create a temporary directory
            tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

            # Extract the zip file
            zip.extractall(tmpdir)

            recursive.call_uforia_recursive(config, rcontext, tmpdir, fullpath)

            # Close the zip file
            zip.close()
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
            print "\nZip file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)
        return None
