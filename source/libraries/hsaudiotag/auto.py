# Created By: Virgil Dupras
# Created On: 2010-12-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

from . import mpeg, mp4, wma, ogg, flac, aiff

ALL_CLASSES = [mp4.File, mpeg.Mpeg, wma.WMADecoder, ogg.Vorbis, flac.FLAC, aiff.File]

EXT2CLASS = {
    u'mp3': mpeg.Mpeg,
    u'wma': wma.WMADecoder,
    u'm4a': mp4.File,
    u'm4p': mp4.File,
    u'ogg': ogg.Vorbis,
    u'flac': flac.FLAC,
    u'aif': aiff.File,
    u'aiff': aiff.File,
    u'aifc': aiff.File,
}

AUDIO_ATTRS = set([u'size', u'duration', u'bitrate', u'sample_rate', u'audio_offset', u'audio_size'])
TAG_ATTRS = set([u'artist', u'album', u'title', u'genre', u'year', u'track', u'comment'])

class File(object):
    u"""Automatically determine a file type and decode it accordingly, providing a unified interface
    to all file types.
    """
    def __init__(self, infile):
        self._set_invalid_attrs()
        f = self._guess_class(infile)
        if f is not None:
            self._set_attrs(f)
        if hasattr(f, u'close'):
            f.close()

    @staticmethod
    def _guess_class(infile):
        if isinstance(infile, basestring):
            # Try a fast path to the right class instead of trying all classes sequencially.
            ext = op.splitext(infile)[1][1:]
            if ext in EXT2CLASS:
                f = EXT2CLASS[ext](infile)
                if f.valid:
                    return f
        for class_ in ALL_CLASSES:
            f = class_(infile)
            if f.valid:
                return f
        else:
            return None

    def _set_attrs(self, f):
        self.valid = True
        self.original = f
        for attrname in AUDIO_ATTRS:
            setattr(self, attrname, getattr(f, attrname))
        tag = f.tag if hasattr(f, u'tag') else f
        if tag is not None:
            for attrname in TAG_ATTRS:
                setattr(self, attrname, getattr(tag, attrname))

    def _set_invalid_attrs(self):
        self.valid = False
        self.original = None
        for attrname in AUDIO_ATTRS:
            setattr(self, attrname, 0)
        for attrname in TAG_ATTRS:
            default = u'' if attrname != u'track' else 0
            setattr(self, attrname, default)
