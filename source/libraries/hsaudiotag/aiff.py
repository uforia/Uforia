# Created By: Virgil Dupras
# Created On: 2008-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

# http://www.cnpbagwell.com/aiff-c.txt

from __future__ import with_statement
import logging
import struct
from io import BytesIO

from .id3v2 import Id3v2
from .util import FileOrPath

HEADER_SIZE = 8

class NotAChunk(Exception):
    pass

# based on stdlib's aifc
_HUGE_VAL = 1.79769313486231e+308
def read_float(s): # 10 bytes
    expon, himant, lomant = struct.unpack('>hLL', s)
    sign = 1
    if expon < 0:
        sign = -1
        expon = expon + 0x8000
    if expon == himant == lomant == 0:
        f = 0.0
    elif expon == 0x7FFF:
        f = _HUGE_VAL
    else:
        expon = expon - 16383
        f = (himant * 0x100000000 + lomant) * pow(2.0, expon - 63)
    return sign * f

class Chunk(object):
    def __init__(self, fp):
        self._fp = fp
        self.position = fp.tell()
        header = fp.read(HEADER_SIZE)
        if len(header) < HEADER_SIZE:
            raise NotAChunk()
        self.type, self.size = struct.unpack('>4si', header)
        if self.size <= 0:
            raise NotAChunk()
        self.data = None

    def read(self):
        self._fp.seek(self.position + HEADER_SIZE)
        self.data = self._fp.read(self.size)


class File(Chunk):
    def __init__(self, infile):
        self.valid = False
        self.tag = None
        self.duration = self.bitrate = self.sample_rate = self.audio_offset = self.audio_size = 0
        with FileOrPath(infile) as fp:
            try:
                Chunk.__init__(self, fp)
                self.read()
                self.valid = self.duration > 0
            except NotAChunk:
                return

    def read(self):
        # the FORM chunk (the main chunk) has 4 bytes for the type, then the subchunks
        self._fp.seek(4, 1)
        while True:
            try:
                chunk = Chunk(self._fp)
            except NotAChunk:
                break
            if chunk.type == 'ID3 ':
                chunk.read()
                self.tag = Id3v2(BytesIO(chunk.data))
            elif chunk.type == 'COMM':
                chunk.read()
                try:
                    channels, frame_count, sample_size, sample_rate = struct.unpack('>hLh10s', chunk.data[:18])
                except struct.error:
                    logging.warning(u'Could not unpack the COMM field %r' % chunk.data)
                    raise
                self.sample_rate = int(read_float(sample_rate))
                self.bitrate = channels * sample_size * self.sample_rate
                self.duration = frame_count // self.sample_rate
            elif chunk.type == 'SSND':
                self.audio_offset = chunk.position + HEADER_SIZE
                self.audio_size = chunk.size
            self._fp.seek(chunk.position + HEADER_SIZE + chunk.size)
