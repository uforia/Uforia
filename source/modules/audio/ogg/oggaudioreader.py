'''
Created on 28 feb. 2013

@author: Jimmy van den Berg
'''

# This is the audio module for .ogg

# TABLE: Artist:LONGTEXT, Album:LONGTEXT, Title:LONGTEXT, Genre:LONGTEXT, Year:INT(4), Track:INT, Comment:LONGTEXT, DurationInSeconds:DOUBLE, BitRate:INT, SampleRate:INT, AudioFileSize:INT, AudioOffset:INT

import sys
import traceback
from hsaudiotag import auto


def process(fullpath, config, columns=None):
        # Try to parse .ogg data
        try:
            # Read the .ogg file
            ogg_file = auto.File(fullpath)

            # Check if .ogg file is readed correctly
            if ogg_file.valid:

                # Store audio data in list
                assorted = [
                    ogg_file.title,
                    ogg_file.artist,
                    ogg_file.album,
                    ogg_file.genre,
                    ogg_file.year,
                    ogg_file.track,
                    ogg_file.comment,
                    ogg_file.duration,
                    ogg_file.sample_rate,
                    ogg_file.audio_size,
                    ogg_file.bitrate,
                    ogg_file.audio_offset]

                # delete the ogg_file variable
                del ogg_file

                # Make sure we stored exactly the same amount of columns as
                # specified!!
                assert len(assorted) == len(columns)

                # Print some data that is stored in
                # the database if debug is true
                if config.DEBUG:
                    print "\nOGG file data:"
                    for i in range(0, len(assorted)):
                        print "%-18s %s" % (columns[i], assorted[i])
                    print

                # Store in database
                return assorted
            else:
                return None

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
