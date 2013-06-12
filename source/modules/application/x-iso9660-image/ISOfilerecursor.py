# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# TABLE: Bootrec_Type:INT, Bootrec_Identifier:TEXT, Bootrec_Version:INT, Bootrec_BootSysId:TEXT, Bootrec_Id:BLOB, Bootrec_BootSysUse:BLOB, typecode:INT, ident:TEXT, version:INT, unused:INT, sysid:INT, volid:TEXT, volspacesize:INT, unusedfield:INT,volsetsize:INT, volseqno:INT, logblocksize:INT, pathtablesize:INT, locpathtable:INT,locoptpathtable:INT, loctypeMath:INT, lcoopttypeMpath:INT, rootdirentry:TEXT,volsetid:TEXT, publid:TEXT, dataprepid:TEXT, applid:TEXT, copyfileid:TEXT, abstrfileid:TEXT,bibliofileid:TEXT, volumecraetedt:TEXT, volumemoddt:TEXT, volumeexpdt:TEXT,volumeeffdt:TEXT

import sys
import traceback
import tempfile
import shutil
import os
import imp
import recursive
import struct
from pylzmalib import py7zlib


def _seek_until(file, startstring):
    startstring_pos = 0
    while True:
        b = file.read(1)
        if b == None:
            return False

        if startstring_pos == 0:
            if b == startstring[0]:
                startstring_pos = 1
        else:
            if b == startstring[startstring_pos]:
                startstring_pos += 1
                if startstring_pos >= len(startstring):
                    return True
            else:
                startstring_pos = 0

# \x00CD001
def _get_boot_record(file):
    seek = _seek_until(file, b"\x00CD001")
    if not seek:
        return [None,None,None,None,None,None]

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

    return [type,identifier,version,bootsysid,bootrecid,bootsysuse]

# \x01CD001, \x02CD001, etc
def _get_descriptors(file):
    seek = _seek_until(file, b"\x00CD001")
    if not seek:
        return  [None for i in range(28)]
    
    typecode = 1
    ident =  "CD001"
    version = file.read(1)
    unused = file.read(1)
    sysid = file.read(32)
    volid = file.read(32)
    volspacesize = struct.unpack('i', file.read(4))
    file.read(4)
    unusedfield = 0
    volsetsize = struct.unpack('i', file.read(4))
    volseqno = struct.unpack('i', file.read(4))
    logblocksize = struct.unpack('i', file.read(4))
    pathtablesize = struct.unpack('i', file.read(4))
    file.read(4)
    locpathtable = struct.unpack('i', file.read(4))
    locoptpathtable = struct.unpack('i', file.read(4))
    loctypeMpath = struct.unpack('>i', file.read(4))
    locopttypeMpath = struct.unpack('>i', file.read(4))
    rootdirentry = file.read(34)
    volsetid = file.read(128)
    publid = file.read(128)
    dataprepid = file.read(128)
    applid = file.read(128)
    copyfileid = file.read(38)
    abstrfileid = file.read(36)
    bibliofileid = file.read(37)
    volumecreatedt = file.read(17)
    volumemoddt = file.read(17)
    volumeexpdt = file.read(17)
    volumeeffdt = file.read(17)
    
    return [typecode, ident, version, unused, sysid, volid,volspacesize, unusedfield,
            volsetsize, volseqno, logblocksize, pathtablesize, locpathtable,
            locoptpathtable, loctypeMpath, locopttypeMpath, rootdirentry,
            volsetid, publid, dataprepid, applid, copyfileid, abstrfileid,
            bibliofileid, volumecreatedt, volumemoddt, volumeexpdt,
            volumeeffdt]
            
# \xFFCD001
def _get_terminator(file):
    return []

def _get_volume_descriptors(file):
    result = []
    result += _get_boot_record(file)

    file.seek(0)
    while True:
        descriptor = _get_descriptors(file)
        if descriptor == None:
            break
        else:
            result += descriptor

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
