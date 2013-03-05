#!/usr/bin/env python

# This is the module for audio

#TABLE: ARTIST:LONGTEXT, TITLE:LONGTEXT, CHANNELS:LONGTEXT, COMMENT:LONGTEXT, DURATION:INT(3), GENRE:LONGTEXT, SAMPLERATE:INT(3), SIZE:INT(3), TRACK:INT(3), VALID:LONGTEXT, YEAR:INT(3), ALBUM:LONGTEXT, AUDIO_SIZE:INT(3)

# import for external lib hsaudiotag
# This lib is used for the audio module, so please install it with the following command: pip install eyeD3
from hsaudiotag import wma
import imp
import sys

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise


def process(fullpath):
    try:
        myfile = wma.WMADecoder(fullpath)
        if config.DEBUG:
            print "\nAudio file data:"
            print "Artist:        %s" % myfile.artist
            print "Title:         %s" % myfile.title
            print "Channels:      %s" % myfile.channels
            print "Comment:       %s" % myfile.comment
            print "Duration:      %s" % myfile.duration
            print "Genre:         %s" % myfile.genre
            print "Sample Rate:   %s" % myfile.sample_rate
            print "Size:          %s" % myfile.size
            print "Track:         %s" % myfile.track
            print "Valid:         %s" % myfile.valid
            print "Year:          %s" % myfile.year
            print "Album:         %s" % myfile.album
            print "Audio Size:    %s" % myfile.audio_size
#            print "Bitrate:       %s" % str(myfile.bitrate())
            print

    
    except:
        print "An error occured while parsing audio data: ", sys.exc_info()
        
    return (myfile.artist, myfile.title, myfile.channels,  myfile.comment,  myfile.duration,  myfile.genre,  myfile.sample_rate,  myfile.size, myfile.track, myfile.valid, myfile.year)
       