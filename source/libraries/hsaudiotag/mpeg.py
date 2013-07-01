# Created By: Virgil Dupras
# Created On: 2004/12/10
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

from __future__ import with_statement
from . import id3v1
from . import id3v2
import struct
from struct import unpack

from .util import tryint, FileOrPath

HEADER_SIZE = 4

ID_MPEG1 = 3
ID_MPEG2 = 2
ID_MPEG25 = 0

ID_LAYER1 = 3
ID_LAYER2 = 2
ID_LAYER3 = 1

MPEG_SYNC = 0xffe00000  # 11 bits set
MPEG_PAD = 0x200  # pad flag mask (pos 20)

BR_NULL = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

BR_M1_L1 = (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, 0)
BR_M1_L2 = (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384, 0)
BR_M1_L3 = (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0)
BR_M2_L1 = (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256, 0)
BR_M2_L23 = (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0)

BR_M1 = (BR_NULL, BR_M1_L3, BR_M1_L2, BR_M1_L1)
BR_M2 = (BR_NULL, BR_M2_L23, BR_M2_L23, BR_M2_L1)
BR_NULLS = (BR_NULL, BR_NULL, BR_NULL, BR_NULL)

BR_LIST = (BR_M2, BR_NULLS, BR_M2, BR_M1)

SR_NULL = (0, 0, 0, 0)

SR_M1 = (44100, 48000, 32000, 0)
SR_M2 = (22050, 24000, 16000, 0)
SR_M25 = (11025, 12000, 8000, 0)

SR_LIST = (SR_M25, SR_NULL, SR_M2, SR_M1)

SPF_NULL = (0, 0, 0, 0)

SPF_M1 = (0, 1152, 1152, 384)
SPF_M2 = (0, 576, 1152, 384)

SPF_LIST = (SPF_M2, SPF_NULL, SPF_M2, SPF_M1)

MPEG_CM_STEREO = 0;
MPEG_CM_JOINT_STEREO = 1;
MPEG_CM_DUAL_CHANNEL = 2;
MPEG_CM_MONO = 3;
MPEG_CM_UNKNOWN = 4;

MAX_SEEK_BYTES = 4096

def get_vbr_offset(version, channel_mode):
    # Depending on mpeg version and mode, the VBR header will be at a different offset
    # after the mpeg header.
    if version == ID_MPEG1:
        if channel_mode == MPEG_CM_MONO:
            return 17
        else:
            return 32
    else:
        if channel_mode == MPEG_CM_MONO:
            return 9
        else:
            return 17

def get_vbr_coefficient(version, layer):
    if version == ID_MPEG1:
        if layer == ID_LAYER1:
            return 48
        else:
            return 144
    else:
        if layer == ID_LAYER1:
            return 24
        elif layer == ID_LAYER2:
            return 144
        else:
            return 72

class MpegFrameHeader(object):
    def __init__(self, data):
        # data = HEADER_SIZE bytes integer
        self.valid = False
        self.mpeg_id = 0
        self.layer = 0
        self.channel_mode = MPEG_CM_UNKNOWN
        self.bitrate = 0
        self.sample_rate = 0
        self.sample_count = 0
        self.padding_size = 0
        self.size = 0
        if (data & MPEG_SYNC) == MPEG_SYNC:
            self.valid = True
            self.mpeg_id = (data >> 19) & 0x3
            self.layer = (data >> 17) & 0x3
            self.channel_mode = (data >> 6) & 0x3
            br_id = (data >> 12) & 0xf
            fr_id = (data >> 10) & 0x3
            self.bitrate = BR_LIST[self.mpeg_id][self.layer][br_id]
            self.sample_rate = SR_LIST[self.mpeg_id][fr_id]
            self.sample_count = SPF_LIST[self.mpeg_id][self.layer]
            if data & MPEG_PAD:
                self.padding_size = (4 if self.layer == ID_LAYER1 else 1)
            else:
                self.padding_size = 0
            if self.sample_count and self.bitrate and self.sample_rate:
                sc = self.sample_count
                sr = self.sample_rate
                br = self.bitrate
                pad = self.padding_size
                self.size = (((sc // 8) * br * 1000) // sr) + pad
            else:
                self.valid = False


class XingHeader(object):
    def __init__(self, data):  # data is a 128 bytes str
        self.valid = data[:4] == 'Xing'
        self.frames = unpack('!I', data[8:12])[0]
        self.size = unpack('!I', data[12:16])[0]
        self.scale = data[119]

class FhgHeader(object):
    def __init__(self, data):
        self.valid = data[:4] == 'VBRI'
        self.frames = unpack('!I', data[14:18])[0]
        self.size = unpack('!I', data[10:14])[0]
        self.scale = unpack('B', data[9:10])[0]

class ComputedVBRHeader(object):
    def __init__(self, frame_browser):
        self.valid = True
        self.frames, self.size = frame_browser.stats()


class FrameBrowser(object):
    def __init__(self, fp):
        self.fp = fp
        self.frame_index = 0
        if not self._read():
            self._seek()
        self.initial_position = self.position

    def _read(self):
        self.position = tryint(self.fp.tell())
        data = self.fp.read(HEADER_SIZE)
        try:
            self.frame = MpegFrameHeader(unpack("!I", data)[0])
        except struct.error:
            self.frame = MpegFrameHeader(0)
        return self.frame.valid

    def _seek(self):
        # A mpeg header is 11 set bits. Which means that there is a \xff char followed by a char
        # that is \xe0 or more.
        self.fp.seek(self.position, 0)
        data = self.fp.read(MAX_SEEK_BYTES)
        tag_index = data.find(id3v2.ID_ID3)
        if tag_index > -1:
            self.fp.seek(self.position + tag_index, 0)
            h = id3v2.Header(self.fp)
            if h.valid:
                self.position += tag_index + h.tagsize
                return self._seek()
        index = data.find('\xff')
        while (index > -1):
            try:
                result = MpegFrameHeader(unpack('!I', data[index:index + HEADER_SIZE])[0])
                if result.valid:
                    nextindex = index + result.size
                    try:
                        next = MpegFrameHeader(unpack('!I', data[nextindex:nextindex + HEADER_SIZE])[0])
                        if next.valid:
                            self.position += index
                            self.frame = result
                            return True
                    except struct.error:
                        pass
                index = data.find('\xff', index + 1)
            except struct.error:
                index = -1
        return False

    def first(self):
        self.fp.seek(self.initial_position, 0)
        self.frame_index = 0
        self._read()
        return self.frame

    def next(self):
        if self.frame.valid:
            self.fp.seek(self.position + self.frame.size, 0)
            self._read()
            self.frame_index += 1
        return self.frame

    def stats(self):
        u"""Iterates over all frames and return (frame_count, total_size)"""
        self.first()
        size = self.frame.size
        while self.next().valid:
            size += self.frame.size
        return (self.frame_index, size)


def get_vbr_info(fp, b):
    fheader = b.frame
    vbr_offset = get_vbr_offset(fheader.mpeg_id, fheader.channel_mode)
    fp.seek(vbr_offset + 4, 1)
    vbr_id = fp.read(4)
    fp.seek(-4, 1)
    if vbr_id == 'Xing':
        return XingHeader(fp.read(128))
    if vbr_id == 'VBRI':
        return FhgHeader(fp.read(18))
    br = b.frame.bitrate
    for i in xrange(4):
        if b.next().bitrate != br:
            return ComputedVBRHeader(b)

class Mpeg(object):
    def __init__(self, infile):
        with FileOrPath(infile) as fp:
            self.id3v1 = id3v1.Id3v1(fp)
            self.id3v2 = id3v2.Id3v2(fp)
            if self.id3v2.exists and (self.id3v2.position == id3v2.POS_BEGIN):
                start_offset = self.id3v2.size
            else:
                start_offset = 0
            fp.seek(start_offset, 0)
            b = FrameBrowser(fp)
            self._frameheader = b.frame
            self.audio_offset = b.position
            fp.seek(b.position, 0)  # Needed for VBR seeking
            self.vbr = get_vbr_info(fp, b)
            fp.seek(0, 2)
            self.size = tryint(fp.tell())
            if self.bitrate:
                # (audio_size * 8) / (bitrate * 1000) == audio_size / (bitrate * 125)
                self.duration = self.audio_size // (self.bitrate * 125)
                # 'and self.id3v2.duration' is there to avoid reading the mpeg frames when there is no TLEN in the tag.
                if self.id3v2.exists and self.id3v2.duration and (self.id3v2.duration != self.duration):
                    # Tag duration and guessed durations are wrong. Read all frames
                    frames, size = b.stats()
                    self.duration = size // (self.bitrate * 125)
            else:
                self.duration = 0
            self.valid = self._frameheader.valid

    #--- Properties
    @property
    def tag(self):
        if self.id3v2.exists:
            return self.id3v2
        elif self.id3v1.exists:
            return self.id3v1

    @property
    def audio_size(self):
        result = self.size - self.id3v1.size - self.audio_offset
        if self.id3v2.position == id3v2.POS_END:
            result -= self.id3v2.size
        return result

    @property
    def bitrate(self):
        if self.vbr and (self.vbr.frames > 0):
            coeff = get_vbr_coefficient(self._frameheader.mpeg_id, self._frameheader.layer)
            pad = self._frameheader.padding_size
            sr = self._frameheader.sample_rate
            size_per_frame = self.vbr.size // self.vbr.frames
            return ((size_per_frame - pad) * sr) // (coeff * 1000)
        else:
            return self._frameheader.bitrate

    @property
    def sample_rate(self):
        return self._frameheader.sample_rate
