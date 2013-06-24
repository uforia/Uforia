# Created By: Virgil Dupras
# Created On: 2004/12/09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from __future__ import with_statement
import io
import struct
import re

from .util import cond, tryint, FileOrPath
from .genres import genre_by_index

ID_ID3 = 'ID3'
ID_3DI = '3DI'
# The id3 flags are backwards
FLAG_UNSYNCH = 1 << 7
FLAG_EXT_HEADER = 1 << 6
FLAG_EXPERIMENTAL = 1 << 5
FLAG_FOOTER = 1 << 4

POS_BEGIN = 0
POS_END = 1

re_numeric_genre = re.compile(ur'^\(?(\d{1,3})')
re_frame_type = re.compile(ur'[A-Z0-9]{3,4}')

def _read_id3_size(rawsize, syncsafe=True):
    if len(rawsize) != 4:
        return 0
    if syncsafe:
        b1, b2, b3, b4 = (ord(b) for b in rawsize)
        return (b1 * 0x200000) + (b2 * 0x4000) + (b3 * 0x80) + b4
    else:
        return struct.unpack('!i', rawsize)[0]

STRING_ENCODINGS = {0: u'iso-8859-1', 1: u'utf-16', 2: u'utf-16be', 3: u'utf-8'}

def _read_id3_string(s, stringtype, nullreplace=u'\n'):
    encoding = STRING_ENCODINGS[stringtype]
    if stringtype == 1:
        # This is a safekeeping code. Under normal circumstances, it shouldn't
        # happen to have a \0 or a second BOM or no BOM in a type 1 string
        le = '\xff\xfe'
        be = '\xfe\xff'
        bom = s[:2]
        if bom in (le, be):
            therest = s[2:].replace(be, '').replace(le, '')
            s = bom + therest
        else:
            s = le + s
    try:
        s = unicode(s, encoding)
    except UnicodeDecodeError:
        try:
            s = unicode(s + '\0', encoding)
        except UnicodeDecodeError:
            s = u''
    if nullreplace != u'\0':
        s = s.replace(u'\0', nullreplace)
    return s

SIZE_HEADER = 10
SIZE_FOOTER = 10

class Header(object):
    def __init__(self, fp, header_id=ID_ID3):
        self.datasize = 0  # size of the data only (extheader + frames)
        self.tagsize = 0  # size of the whole tag (datasize + header + footer)
        self.vmajor = 0
        self.vminor = 0
        self.hflags = 0
        header = fp.read(SIZE_HEADER)
        if header[0:3] != header_id:
            return
        self.vmajor = ord(header[3])
        self.vminor = ord(header[4])
        self.hflags = ord(header[5])
        self.datasize = _read_id3_size(header[6:10], syncsafe=True)
        self.tagsize = self.datasize + SIZE_HEADER
        if FLAG_FOOTER & self.hflags:
            self.tagsize += SIZE_FOOTER

    @property
    def valid(self):
        return self.vmajor > 0


class ExtHeader(object):
    def __init__(self, fp, tagversion):
        # There's no use for the extheader at the moment, so for now, the sole purpose of this class
        # is to skip the size of this header and advance the file descriptor for the rest of the read
        self.size = _read_id3_size(fp.read(4), tagversion > 3)
        self.data = fp.read(self.size - 4)


class FrameDataText(object):
    def __init__(self, fp):
        self.text = u''
        stringtype = ord(fp.read(1)[0])
        if stringtype in STRING_ENCODINGS:
            self.text = _read_id3_string(fp.read(), stringtype)

    @staticmethod
    def supports(frameid):
        return frameid.startswith(u'T')


class FrameDataComment(object):
    def __init__(self, fp):
        self._text = (u'', u'')
        stringtype = ord(fp.read(1)[0])
        language = fp.read(3)
        if stringtype in STRING_ENCODINGS:
            text = fp.read()
            text = _read_id3_string(text, stringtype, u'\0')
            self._text = tuple(text.split(u'\0'))

    @staticmethod
    def supports(frameid):
        return frameid.startswith(u'COM')

    @property
    def title(self):
        return self._text[0] if len(self._text) > 0 else u''

    @property
    def comment(self):
        return self._text[1] if len(self._text) > 1 else u''

    @property
    def text(self):
        return self.comment if self.comment else self.title


FRAMEDATA_LIST = [FrameDataText, FrameDataComment]

def _find_frame_data_class(frameid):
    for framedataclass in FRAMEDATA_LIST:
        if framedataclass.supports(frameid):
            return framedataclass

class Id3Frame(object):
    def __init__(self, fp, frame_id, size):
        self.frame_id = frame_id
        self.size = size
        self.rawdata = io.BytesIO(fp.read(size))
        self._data = None

    @property
    def valid(self):
        if self.size == 0:
            return False
        if not re_frame_type.match(self.frame_id):
            return False
        return True

    @property
    def data(self):
        if self._data is None:
            framedataclass = _find_frame_data_class(self.frame_id)
            if framedataclass:
                self._data = framedataclass(self.rawdata)
            else:
                raise NotImplementedError(u'Support for frame \'%s\' is not implemented yet' % self.frame_id)
        return self._data


class Id3v22Frame(Id3Frame):
    def __init__(self, fp):
        frame_id = unicode(fp.read(3), u'ascii', u'replace')
        size = _read_id3_size('\0' + fp.read(3), syncsafe=False)
        Id3Frame.__init__(self, fp, frame_id, size)

class Id3v23Frame(Id3Frame):
    def __init__(self, fp, syncsafe):
        frameid = unicode(fp.read(4), u'ascii', u'replace')
        size = _read_id3_size(fp.read(4), syncsafe=syncsafe)
        flags = fp.read(2)
        Id3Frame.__init__(self, fp, frameid, size)

class Id3v2(object):
    def __init__(self, infile):
        self.position = POS_BEGIN
        self._extheader = None
        self.frames = None
        self._last_read_frame = None
        self._had_large_frame = False
        with FileOrPath(infile) as fp:
            fp.seek(0, 0)
            h = Header(fp)
            if not h.valid:
                try:
                    fp.seek(-SIZE_FOOTER, 2)
                    h = Header(fp, ID_3DI)
                    if h.valid:
                        fp.seek(-h.tagsize, 2)
                        h = Header(fp)
                        self.position = POS_END
                except IOError:
                    pass
            self._header = h
            if self.exists:
                data = io.BytesIO(fp.read(self.data_size))
                if FLAG_EXT_HEADER & self.flags:
                    self._extheader = ExtHeader(data, self._header.vmajor)
                self._read_frames(data)

    #---Private
    def _decode_track(self, track):
        # The track field can either contain a track number or a string in the
        # format <trackno>/<trackcount> (Example: 3/14)
        try:
            return int(track)
        except ValueError:
            if u'/' in track:
                return self._decode_track(track.split(u'/')[0])
            else:
                return 0

    def _get_frame(self, fp):
        if self.version == 2:
            return Id3v22Frame(fp)
        else:
            return Id3v23Frame(fp, self.version > 3)

    def _read_frames(self, fp):
        offset = fp.tell()
        self.frames = {}
        frame = self._get_frame(fp)
        while frame.valid:
            if (self._last_read_frame is not None) and (self._last_read_frame.size > 0x7f):
                self._had_large_frame = True
            self._last_read_frame = frame
            self.frames[frame.frame_id] = frame
            frame = self._get_frame(fp)
        if (self._last_read_frame is not None) and (self._last_read_frame.size > 0x7f) and \
            (not self._had_large_frame) and (self.version == 4):
            # probably needs a itunes hack, in any case, this is the first large frame,
            # re-reading can't hurt.
            self._header.vmajor = 3
            fp.seek(offset)
            self._read_frames(fp)

    def _get_frame_data(self, frame_id):
        if frame_id in self.frames:
            return self.frames[frame_id].data

    def _get_frame_text(self, frame_id):
        result = self._get_frame_data(frame_id)
        return getattr(result, u'text', u'').strip()

    def _get_frame_text_line(self, frame_id):
        result = self._get_frame_text(frame_id)
        return result.replace(u'\n', u' ').replace(u'\r', u' ')

    #--- Properties
    size = property(lambda self: self._header.tagsize)
    data_size = property(lambda self: self._header.datasize)
    exists = property(lambda self: self._header.valid)
    flags = property(lambda self: self._header.hflags)
    version = property(lambda self: self._header.vmajor)

    @property
    def album(self):
        frame_id = cond(self.version >= 3, u'TALB', u'TAL')
        return self._get_frame_text_line(frame_id)

    @property
    def artist(self):
        frame_id = cond(self.version >= 3, u'TPE1', u'TP1')
        return self._get_frame_text_line(frame_id)

    @property
    def comment(self):
        frame_id = cond(self.version >= 3, u'COMM', u'COM')
        return self._get_frame_text(frame_id)

    @property
    def duration(self):
        s = self._get_frame_text(u'TLEN')
        return tryint(s) // 1000

    @property
    def genre(self):
        frame_id = cond(self.version >= 3, u'TCON', u'TCO')
        genre = self._get_frame_text_line(frame_id)
        match = re_numeric_genre.match(genre)
        if match:
            index = int(match.group(1))
            return genre_by_index(index)
        else:
            return genre

    @property
    def title(self):
        frame_id = cond(self.version >= 3, u'TIT2', u'TT2')
        return self._get_frame_text_line(frame_id)

    @property
    def track(self):
        frame_id = cond(self.version >= 3, u'TRCK', u'TRK')
        s = self._get_frame_text_line(frame_id)
        return self._decode_track(s)

    @property
    def year(self):
        frame_id = cond(self.version >= 3, u'TYER', u'TYE')
        return self._get_frame_text_line(frame_id)
