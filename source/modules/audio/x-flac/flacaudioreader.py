# Module for FLAC audio file parsing
#
#TABLE: Length:FLOAT(32)

import sys, traceback
import mutagen, mutagen.flac

def process(fullpath):
    audio = mutagen.flac.FLAC(fullpath)
    return (audio.info.length,)
