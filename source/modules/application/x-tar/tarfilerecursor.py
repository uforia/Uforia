# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Stores tar file metadata and starts Uforia recursively on the files
# inside the tar file

# TABLE: file_names:LONGTEXT, total_files:INT, member_info:LONGTEXT

import sys
import traceback
import os
import tempfile
import stat
import recursive
import tarfile


def process(fullpath, config, rcontext, columns=None):
    try:
        # Open the tar file
        tar = tarfile.open(fullpath)

        # Get tar metadata
        assorted = [tar.getnames(), len(tar.getnames())]

        # Create an array with the the contents of the TarInfo structure
        member_info = []
        for member in tar.getmembers():
            member_dict = {}
            wanted_attributes = ['name',
                                 'size',
                                 'mtime',
                                 'mode',
                                 'type',
                                 'linkname',
                                 'uid',
                                 'gid',
                                 'uname',
                                 'gname']
            for attribute in wanted_attributes:
                member_dict[attribute] = getattr(member, attribute)
            member_info.append(member_dict)

        assorted.append(member_info)

        # Try to extract the content of the tar file.
        tmpdir = None
        try:
            # Create a temporary directory
            tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

            # Extract the tar file
            tar.extractall(tmpdir)

            # Close the tar file
            tar.close()

            recursive.call_uforia_recursive(config, rcontext, tmpdir, fullpath)
        except:
            traceback.print_exc(file=sys.stderr)

        if tmpdir != None:
            # Delete the temporary directory, proceed even if it causes
            # an error.
            # Do not use shutils because it may cause permission denied
            # errors as tar preserves permissions.
            try:
                for root, dirs, files in os.walk(tmpdir, topdown=False):
                    for name in files:
                        filename = os.path.join(root, name)
                        os.chmod(filename, stat.S_IWUSR)
                        os.remove(filename)
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
            except:
                traceback.print_exc(file=sys.stderr)

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nTar file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)
        return None
