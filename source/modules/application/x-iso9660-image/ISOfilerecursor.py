# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# TABLE: bootrec_type:INT, bootrec_identifier:TEXT, bootrec_version:INT, bootrec_bootsysid:TEXT, bootrec_id:BLOB, bootrec_bootsysuse:BLOB, volumedescriptors:LONGTEXT, termtype:INT, termidentifier:TEXT, termversion:INT

import sys
import traceback
import tempfile
import shutil
import os
import imp
import recursive
import struct
import py7zlib


def _seek_until(file, startstring):
    """
    Seek until startstring is found in file. Reads in single blocks of
    16 bytes.
    """
    startstring_pos = 0
    while True:
        bytes = file.read(16)
        if bytes == "":
            return False
        elif bytes.startswith(startstring):
            return True


def _get_boot_record(file):
    """
    Get the ISO boot record.
    http://wiki.osdev.org/ISO_9660#The_Boot_Record
    """
    seek = _seek_until(file, b"\x00CD001")
    if not seek:
        return [None for i in range(6)]

    type = 0
    identifier = "CD001"
    version = 0
    bootsysid = ""
    bootrecid = ""
    bootsysuse = ""

    version, = struct.unpack("b", file.read(1))
    bootsysid = file.read(32)
    bootrecid = file.read(32)
    bootsysuse = file.read(1977)

    return [type, identifier, version, bootsysid, bootrecid, bootsysuse]


def _get_descriptor(index, file):
    """
    Get the volume descriptor with index.
    http://wiki.osdev.org/ISO_9660#The_Primary_Volume_Descriptor
    """
    seek = _seek_until(file, struct.pack('b', index) + b"CD001")
    if not seek:
        return None

    descriptor = {}
    descriptor["typecode"] = 1
    descriptor["ident"] = "CD001"
    descriptor["version"] = file.read(1)
    descriptor["unused"] = file.read(1)
    descriptor["sysid"] = file.read(32)
    descriptor["volid"] = file.read(32)
    descriptor["volspacesize"] = struct.unpack('i', file.read(4))[0]
    file.read(4)
    descriptor["unusedfield"] = file.read(8)
    descriptor["volsetsize"] = struct.unpack('h', file.read(2))[0]
    file.read(2)
    descriptor["volseqno"] = struct.unpack('h', file.read(2))[0]
    file.read(2)
    descriptor["logblocksize"] = struct.unpack('h', file.read(2))[0]
    file.read(2)
    descriptor["pathtablesize"] = struct.unpack('i', file.read(4))[0]
    file.read(4)
    descriptor["locpathtable"] = struct.unpack('i', file.read(4))[0]
    descriptor["locoptpathtable"] = struct.unpack('i', file.read(4))[0]
    descriptor["loctypeMpath"] = struct.unpack('>i', file.read(4))[0]
    descriptor["locopttypeMpath"] = struct.unpack('>i', file.read(4))[0]
    descriptor["rootdirentry"] = file.read(34)
    descriptor["volsetid"] = file.read(128)
    descriptor["publid"] = file.read(128)
    descriptor["dataprepid"] = file.read(128)
    descriptor["applid"] = file.read(128)
    descriptor["copyfileid"] = file.read(38)
    descriptor["abstrfileid"] = file.read(36)
    descriptor["bibliofileid"] = file.read(37)
    descriptor["volumecreatedt"] = file.read(17)
    descriptor["volumemoddt"] = file.read(17)
    descriptor["volumeexpdt"] = file.read(17)
    descriptor["volumeeffdt"] = file.read(17)
    descriptor["filestructver"] = struct.unpack('b', file.read(1))[0]
    descriptor["unused2"] = struct.unpack('b', file.read(1))[0]
    descriptor["appused"] = file.read(512)
    descriptor["reserved"] = file.read(653)
    return descriptor


def _get_terminator(file):
    """
    Get the volume description set terminator.
    http://wiki.osdev.org/ISO_9660#Volume_Descriptor_Set_Terminator
    """
    seek = _seek_until(file, b"\x00CD001")
    if not seek:
        return  [None for i in range(3)]
    tertype = file.read(1)
    teridentifier = "CD001"
    terversion = 1
    return [tertype, teridentifier, terversion]


def _get_volume_descriptors(file):
    """
    Get all volume descriptors from file (including boot and
    termination).
    """
    result = []
    result += _get_boot_record(file)

    file.seek(0)
    i = 1
    descriptors = []
    while True:
        descriptor = _get_descriptor(i, file)
        i += 1
        if descriptor == None:
            break
        else:
            descriptors.append(descriptor)
    result.append(descriptors)

    file.seek(0)
    result += _get_terminator(file)
    return result


def process(fullpath, config, rcontext, columns=None):
    # Try to parse 7z data
    try:
        # Get instance of 7z module
        zip_module = imp.load_source('7zfilerecursor',
                                     'modules/application/' +
                                     'x-7z-compressed/7zfilerecursor.py')

        file = open(fullpath, 'rb')
        assorted = _get_volume_descriptors(file)
        file.close()

        # Try to extract the content of the 7zip file.
        try:
            # Create a temporary directory
            tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

            # Extract the 7zip file
            zip_module._extractall(fullpath, tmpdir)

            recursive.call_uforia_recursive(config, rcontext, tmpdir, fullpath)
        except:
            traceback.print_exc(file=sys.stderr)

        # Delete the temporary directory, proceed even if it causes
        # an error
        try:
            shutil.rmtree(tmpdir)
        except:
            traceback.print_exc(file=sys.stderr)

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)

        # Store values in database so not the whole application crashes
        return None
