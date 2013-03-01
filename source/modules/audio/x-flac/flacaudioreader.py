'''
Created on 26 feb. 2013

@author: Marcin Koziuk
'''

# Module for FLAC audio file parsing
#
#TABLE: Length:REAL, SampleRate:BIGINT, TotalSamples:BIGINT, Channels:INT, BPS:INT, Md5Sig:LONGTEXT, MinBlocksize:BIGINT, MaxBlocksize:BIGINT, MinFramesize:BIGINT, MaxFrameSize:BIGINT, Album:LONGTEXT, Artist:LONGTEXT, Title:LONGTEXT, Comment:LONGTEXT, Date:LONGTEXT, TrackNumber:LONGTEXT, Pictures:LONGTEXT, SeekTable:LONGTEXT, CueSheets:LONGTEXT, Unknown:LONGTEXT

import sys, traceback, imp, json
import mutagen, mutagen.flac

try:
    config = imp.load_source('config','include/config.py')
except:
    raise

def lookup_case_insensitive(dict, key):
    """
    Helper function to lookup a key in a dictionary, disregarding the
    case sensitivity. This is an O(n) operation, unlike normal dict
    lookup.
    Returns both the value and the name of the real key. If the key
    is not found None will be returned twice.
    """
    key = key.lower()
    for caseKey, value in dict.items():
        if caseKey.lower() == key:
            return value, caseKey
    return None, None

def process(fullpath, columns=None):
    """
    Uses the mutagen library to parse all FLAC metadata.
    Parses: STREAMINFO, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE
    (http://flac.sourceforge.net/format.html#format_overview)
    """
    try:
        audio = mutagen.flac.FLAC(fullpath)

        # Source of these properties: flac.py from mutagen (StreamInfo class) 
        assorted = [
            audio.info.length,
            audio.info.sample_rate,
            audio.info.total_samples,
            audio.info.channels,
            audio.info.bits_per_sample,
            audio.info.md5_signature,
            audio.info.min_blocksize,
            audio.info.max_blocksize,
            audio.info.min_framesize,
            audio.info.max_framesize
        ]

        # Append ``popular'' key/values
        popular = [ 'album', 'artist', 'title', 'comment', 'date', 'tracknumber']

        tags = audio.tags.as_dict().copy()
        for key in popular:
            value, key = lookup_case_insensitive(tags, key)

            # Remove known values so they don't show up in the 'Unknown' column
            if key != None:
                del tags[key]
                assorted.append(value[0])
            else:
                assorted.append(None)

        # We can't store the picture itself, but gather the metadata anyways
        picturesinfo = []
        for picture in audio.pictures:
            pictureinfo = {}
            # Source: Picture class in flac.py from mutagen, excluding 'data'
            attrs = ['type', 'mime', 'desc', 'width', 'height', 'depth', 'colors']
            for attr in attrs:
                pictureinfo[attr] = getattr(picture, attr)
            picturesinfo.append(pictureinfo)

        dump = json.dumps(picturesinfo)
        assorted.append(dump)

        # Encoded seektable
        dump = json.dumps(audio.seektable.seekpoints) if audio.seektable != None else '{}'
        assorted.append(dump)

        # Encoded cue sheets
        cuedata = {}

        if audio.cuesheet != None:
            # Source: CueSheet class in flac.py from mutagen
            attrs = ['media_catalog_number', 'lead_in_samples', 'compact_disc' ]
            for attr in attrs:
                cuedata[attr] = getattr(audio.cuesheet, attr)

            cuedata['tracks'] = []
            for track in audio.cuesheet.tracks:
                cuedatatrack = {}
                attrs = ['track_number', 'start_offset', 'isrc', 'type', 'pre_emphasis', 'indexes']
                for attr in attrs:
                    cuedatatrack[attr] = getattr(track, attr)
                cuedata['tracks'].append(cuedatatrack)

        dump = json.dumps(cuedata)
        assorted.append(dump)

        # Encode the rest of the tag metadata
        dump = json.dumps(tags, ensure_ascii=False, encoding="utf-8", sort_keys=True)
        assorted.append(dump)

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        if config.DEBUG:
            print "\nFLAC file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i]+':', assorted[i])

        return assorted
    except:
        # Show traceback, since the exception is normally hidden because
        # we operate in another process.
        traceback.print_exc(sys.stderr)
        return None