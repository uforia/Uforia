# Created By: Virgil Dupras
# Created On: 2004/12/20
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from __future__ import with_statement
import struct
from struct import unpack
from io import BytesIO

from .util import FileOrPath

#Object IDs
WMA_ID_SIZE = 16
WMA_OB_HEADER_SIZE = 20 #ID + Size
WMA_HEADER_ID                       = '\x30\x26\xb2\x75\x8e\x66\xcf\x11\xa6\xd9\x00\xaa\x00\x62\xce\x6c'
WMA_DATA_ID                         = '\x36\x26\xb2\x75\x8e\x66\xcf\x11\xa6\xd9\x00\xaa\x00\x62\xce\x6c'
WMA_FILE_PROPERTIES_ID              = '\xa1\xdc\xab\x8c\x47\xa9\xcf\x11\x8e\xe4\x00\xc0\x0c\x20\x53\x65'
WMA_STREAM_PROPERTIES_ID            = '\x91\x07\xdc\xb7\xb7\xa9\xcf\x11\x8e\xe6\x00\xc0\x0c\x20\x53\x65'
WMA_CONTENT_DESCRIPTION_ID          = '\x33\x26\xb2\x75\x8e\x66\xcf\x11\xa6\xd9\x00\xaa\x00\x62\xce\x6c'
WMA_EXTENDED_CONTENT_DESCRIPTION_ID = '\x40\xa4\xd0\xd2\x07\xe3\xd2\x11\x97\xf0\x00\xa0\xc9\x5e\xa8\x50'
WMA_STREAM_BITRATE_PROPERTIES_ID    = '\xce\x75\xf8\x7b\x8d\x46\xd1\x11\x8d\x82\x00\x60\x97\xc9\xa2\xb2'

# Names of supported comment fields
TITLE = 'WM/TITLE'
ARTIST = 'WM/AUTHOR'
ALBUM = 'WM/ALBUMTITLE'
TRACK = 'WM/TRACK'
YEAR = 'WM/YEAR'
GENRE = 'WM/GENRE'
DESCRIPTION = 'WM/DESCRIPTION'

#Max. number of characters in tag field
WMA_MAX_STRING_SIZE = 250;

class WMADecoder(object):
    def __init__(self, infile):
        with FileOrPath(infile) as fp:
            self._read_file(fp)

    #--- Private
    def _decode_string(self, s):
        try:
            return s.decode(u'utf-16-le')[:-1]
        except UnicodeDecodeError:
            try:
                return (s + '\0').decode(u'utf-16-le')[:-1]
            except UnicodeDecodeError:
                return u''

    def _read_file_prop(self, data):
        data.seek(48)
        play_time1, play_time2 = unpack('<2I', data.read(8)) # in 100-nanosec increment
        play_time = (play_time1 << 32) + play_time2
        # For some reason I have to remove 2 seconds
        self.duration = (play_time // 10000000)
        data.seek(80)
        [self._max_br] = unpack('<i', data.read(4))

    def _read_stream_prop(self, data):
        data.seek(60)
        self.channels, self.sample_rate, self._avg_bytes_per_second = unpack("<hii", data.read(10))

    def _read_streambitrate_prop(self, data):
        data.seek(8)
        [avg_br] = unpack("<i", data.read(4))
        self._avg_br = avg_br // 8

    def _read_content_desc(self, data):
        #There are 6 fields in this object, and the size of the 6 objects
        #are at the beginning of the object
        sizes = unpack("<7h", data.read(14))
        fields = [self._decode_string(data.read(size)) if size > 0 else u'' for size in sizes]
        if TITLE not in self._fields:
            self._fields[TITLE] = fields[2]
        if ARTIST not in self._fields:
            self._fields[ARTIST] = fields[3]

    def _read_ext_content(self, data):
        data.seek(4, 1)
        [field_count] = unpack("<h", data.read(2))
        for i in xrange(field_count):
            [name_size] = unpack("<h", data.read(2))
            try:
                field_name = self._decode_string(data.read(name_size)).encode().upper()
            except UnicodeEncodeError:
                field_name = u''
            data_type, data_size = unpack("<2h", data.read(4))
            if data_type == 0: # string
                field_data = self._decode_string(data.read(data_size))
            elif data_type == 3: # int
                [field_data] = unpack("<i", data.read(4))
            else:
                field_data = u''
                data.seek(data_size, 1)
            self._fields[field_name] = field_data

    def _read_file(self, fp):
        #private init
        self.valid = False
        fp.seek(0, 2)
        self.size = fp.tell()
        fp.seek(0, 0)
        self.audio_offset = 0
        self.audio_size = 0
        self.duration = 0
        self.channels = 0
        self.sample_rate = 0
        self.artist = u''
        self.album = u''
        self.title = u''
        self.genre = u''
        self.comment = u''
        self.year = u''
        self.track = 0
        self._max_br = 0
        self._avg_br = 0
        self._avg_bytes_per_second = 0
        self._fields = {}
        functions = {
            WMA_FILE_PROPERTIES_ID: self._read_file_prop,
            WMA_STREAM_PROPERTIES_ID: self._read_stream_prop,
            WMA_CONTENT_DESCRIPTION_ID: self._read_content_desc,
            WMA_EXTENDED_CONTENT_DESCRIPTION_ID: self._read_ext_content,
            WMA_STREAM_BITRATE_PROPERTIES_ID: self._read_streambitrate_prop,
        }
        try:
            if fp.read(WMA_ID_SIZE) == WMA_HEADER_ID:
                fp.seek(8, 1)
                [item_count] = unpack("<i", fp.read(4))
                fp.seek(2, 1)
                self.valid = True
                for i in xrange(item_count):
                    item_id = fp.read(WMA_ID_SIZE)
                    [item_size] = unpack("<i", fp.read(4))
                    if item_id in functions:
                        functions[item_id](BytesIO(fp.read(item_size - WMA_OB_HEADER_SIZE)))
                    else:
                        fp.seek(item_size - WMA_OB_HEADER_SIZE, 1)
                self.artist = self._fields.get(ARTIST, u'')
                self.album = self._fields.get(ALBUM, u'')
                self.title = self._fields.get(TITLE, u'')
                self.genre = self._fields.get(GENRE, u'')
                self.comment = self._fields.get(DESCRIPTION, u'')
                self.year = self._fields.get(YEAR, u'')
                try:
                    self.track = self._fields[TRACK] + 1
                except (TypeError, KeyError):
                    self.track = 0
                if fp.read(WMA_ID_SIZE) == WMA_DATA_ID:
                    self.audio_size = unpack("<i", fp.read(4))[0] - WMA_OB_HEADER_SIZE
                    self.audio_offset = fp.tell()
                else:
                    self.audio_offset = fp.tell() - WMA_ID_SIZE
                    self.audio_size = self.size - self.audio_offset
        except struct.error:
            self.valid = False

    @property
    def bitrate(self):
        return (self._avg_br * 8) // 1000
