'''
Created on 19 mrt. 2013

@author: Ramon
'''

# TABLE: Signature:LONGTEXT, Version:INT, TypeFlags:INT, DataOffSet:INT, ExtraDataLen:INT, ExtraData:INT

import sys
import imp
import traceback
import os
import flvlib
from flvlib import tags
from struct import unpack
from datetime import datetime

# Tag types
AUDIO = 8
VIDEO = 9
META = 18
UNDEFINED = 0


def process(fullpath, config, rcontext, columns=None):
    """
    Pass the filename of an flv file and it will return a dictionary of meta
    data.
    """

    assorted = []
    try:
        # Lock on to the file
        file = open(fullpath, 'rb')

#        flv = tags.FLV(file)
#        tag_generator = flv.iter_tags()
#        for i, tag in enumerate(tag_generator):
#            # Print the tag information
#            print "#%05d %s" % (i + 1, tag)

        signature = file.read(3)
        assorted.append(signature)
        assert signature == 'FLV', 'Not an flv file'
        version = readbyte(file)
        assorted.append(version)
        typeFlags = readbyte(file)
        assorted.append(typeFlags)
        dataOffset = readint(file)
        assorted.append(dataOffset)
        extraDataLen = dataOffset - file.tell()
        assorted.append(extraDataLen)
        extraData = file.read(extraDataLen)
        assorted.append(extraData)
        readtag(file)
        file.close()


        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nFLV file data:"
            for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i] + ':', assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)

        # Store values in database so not the whole application crashes
        return None


def readtag(file):
        unknown = readint(file)
        tagType = readbyte(file)
        dataSize = read24bit(file)
        timeStamp = read24bit(file)
        unknown = readint(file)
        if tagType == AUDIO:
            print "Can't handle audio tags yet"
        elif tagType == VIDEO:
            print "Can't handle video tags yet"
        elif tagType == META:
            endpos = file.tell() + dataSize
            event = readAMFData(file)
            metaData = readAMFData(file)
            # We got the meta data.
            # Our job is done.
            # We are complete
#            update(metaData)
        elif tagType == UNDEFINED:
            print "Can't handle undefined tags yet"


def readint(file):
        data = file.read(4)
        return unpack('>I', data)[0]


def readshort(file):
        data = file.read(2)
        return unpack('>H', data)[0]


def readbyte(file):
        data = file.read(1)
        return unpack('B', data)[0]


def read24bit(file):
        b1, b2, b3 = unpack('3B', file.read(3))
        return (b1 << 16) + (b2 << 8) + b3


def readAMFData(file, dataType=None):
        if dataType is None:
            dataType = readbyte(file)
        funcs = {
            0: readAMFDouble,
            1: readAMFBoolean,
            2: readAMFString,
            3: readAMFObject,
            8: readAMFMixedArray,
           10: readAMFArray,
           11: readAMFDate}
        func = funcs[dataType](file)
        if callable(func):
            return func()


def readAMFDouble(file):
        return unpack('>d', file.read(8))[0]


def readAMFBoolean(file):
        return readbyte(file) == 1


def readAMFString(file):
        size = readshort(file)
        return file.read(size)


def readAMFObject():
        data = readAMFMixedArray()
        result = object()
        result.__dict__.update(data)
        return result


def readAMFMixedArray(file):
    size = readint(file)
    result = {}
    for i in range(size):
        key = readAMFString(file)
        dataType = readbyte(file)
        if not key and dataType == 9:
            break
        result[key] = readAMFData(file, dataType)
    return result


def readAMFArray(file):
    size = readint(file)
    result = []
    for i in range(size):
        result.append(readAMFData)
    return result


def readAMFDate():
    return datetime.fromtimestamp(readAMFDouble(file))
