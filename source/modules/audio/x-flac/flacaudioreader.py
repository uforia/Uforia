'''
Created on 26 feb. 2013

@author: Marcin Koziuk
'''

# Module for FLAC audio file parsing
#
#TABLE: Length:REAL, SampleRate:BIGINT, TotalSamples:BIGINT, Channels:INT, BPS:INT, Md5Sig:LONGTEXT, MinBlocksize:BIGINT, MaxBlocksize:BIGINT, MinFramesize:BIGINT, MaxFrameSize:BIGINT, Title:LONGTEXT, Version:LONGTEXT, Album:LONGTEXT, TrackNumber:INT, Artist:LONGTEXT, Performer:LONGTEXT, Copyright:LONGTEXT, License:LONGTEXT, Organization:LONGTEXT, Description:LONGTEXT, Genre:LONGTEXT, Date:Date, Location:LONGTEXT, Contact:LONGTEXT, ISRC: LONGTEXT, Unknown:BLOB, Pictures:BLOB, SeekTable:BLOB, CueSheets:BLOB

import sys, traceback, json
import mutagen, mutagen.flac
from PIL import Image

def lookupCaseInsensitive(dict, key):
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

def getStreamInfo(audio):
    """
    Returns the stream information of the audio.
    """
    # Source of these properties: flac.py from mutagen (StreamInfo class)
    return [
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

def getVorbisComments(audio):
    """
    Returns common vorbis comments (now per http://xiph.org/vorbis/doc/v-comment.html)
    The rest of the values are stored in the 'Unknown' field.
    """
    values = []
    common = ['TITLE','VERSION','ALBUM','TRACKNUMBER','ARTIST','PERFORMER','COPYRIGHT','LICENSE','ORGANIZATION','DESCRIPTION','GENRE','DATE','LOCATION','CONTACT','ISRC']
    tags = audio.tags.as_dict().copy()
    for key in common:
        value, key = lookupCaseInsensitive(tags, key)
        # Remove known values so they don't show up in the 'Unknown' column
        if key != None:
            del tags[key]
            values.append(value[0])
        else:
            values.append(None)

    # Dump the rest of the tag metadata
    dump = json.dumps(tags, ensure_ascii=False, encoding="utf-8", sort_keys=True)
    values.append(dump)
    return values


def getPictureInfo(audio):
    """
    Returns JSON-encoded picture metadata, but not the actual pictures.
    """
    picturesinfo = []
    for picture in audio.pictures:
        pictureinfo = {}
        # Source: Picture class in flac.py from mutagen, excluding 'data'
        attrs = ['type', 'mime', 'desc', 'width', 'height', 'depth', 'colors']
        for attr in attrs:
            pictureinfo[attr] = getattr(picture, attr)

        picturesinfo.append(pictureinfo)

    return json.dumps(picturesinfo)


def getSeektable(audio):
    """
    Returns a JSON-encoded version of the file's seek table.
    """
    return json.dumps(audio.seektable.seekpoints) if audio.seektable != None else '{}'

def getCuesheet(audio):
    """
    Returns the embedded cuesheet of the audio file in JSON.
    """
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

    return json.dumps(cuedata)

def process(fullpath, config, columns=None):
    """
    Uses the mutagen library to parse all FLAC metadata.
    Parses: STREAMINFO, SEEKTABLE, VORBIS_COMMENT, CUESHEET, PICTURE
    (http://flac.sourceforge.net/format.html#format_overview)
    """
    try:
        audio = mutagen.flac.FLAC(fullpath)

        assorted = getStreamInfo(audio)
        assorted += getVorbisComments(audio)
        assorted.append(getPictureInfo(audio))
        assorted.append(getSeektable(audio))
        assorted.append(getCuesheet(audio))

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns), \
            "Previously defined column length (%d) is not equal to the length of assorted list (%d)" % (len(columns), len(assorted))

        if config.DEBUG:
            print "\nFLAC file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])

        return assorted
    except:
        # Show traceback, since the exception is normally hidden because
        # we operate in another process.
        traceback.print_exc(sys.stderr)
        return None