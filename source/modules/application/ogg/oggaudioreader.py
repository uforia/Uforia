'''
Created on 28 feb. 2013

@author: Jimmy van den Berg
'''

#!/usr/bin/env python

# This is the audio module for .ogg

#TABLE: Artist:LONGTEXT, Album:LONGTEXT, Title:LONGTEXT, Genre:LONGTEXT, Year:LONGTEXT, Track:LONGTEXT, Comment:LONGTEXT, DurationInSeconds:INT(6), BitRate:INT, SampleRate:INT, AudioFileSize:INT, AudioOffset:INT

import sys, imp
from hsaudiotag import auto

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise

def process(fullpath, columns=None):
        #Try to parse .ogg data
        try:  
            #Read the .ogg file
            oggFile = auto.File(fullpath)
        
            #Check if .ogg file is readed correctly
            if oggFile.valid:
                
                # Print some data that is stored in the database if debug is true
                if config.DEBUG:
                    print "\nOGG file data:"
                    print "Title:        %s" % oggFile.title
                    print "Arist:        %s" % oggFile.artist
                    print "Album:        %s" % oggFile.album
                    print "Genre:        %s" % oggFile.genre
                    print "Year:         %s" % oggFile.year
                    print "Track:        %s" % oggFile.track
                    print "Comment:      %s" % oggFile.comment
                    print "Duration:     %s" % str(oggFile.duration)
                    print "SampleRate:   %s" % str(oggFile.sample_rate)
                    print "AudioSize:    %s" % str(oggFile.audio_size)
                    print "BitRate:      %s" % str(oggFile.bitrate)
                    print "Audio offset: %s" % str(oggFile.audio_offset)
                    print
                
                #Store data in database
                return(oggFile.artist, oggFile.album, oggFile.title, oggFile.genre, oggFile.year, oggFile.track, oggFile.comment, oggFile.duration, oggFile.bitrate, oggFile.sample_rate, oggFile.audio_size, oggFile.audio_offset)
            else:
                return(None, None, None, None, None, None, None, None, None, None, None, None)
        
        except:
            print "An error occured while parsing audio data: ", sys.exc_info()
        
            # Store values in database so not the whole application crashes
            return (None, None, None, None, None, None, None, None, None, None, None, None)
        
        
        