# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

#!/usr/bin/env python

# This is the audio module for WMA

# TABLE: ARTIST:LONGTEXT, TITLE:LONGTEXT, CHANNELS:LONGTEXT, COMMENT:INT, DURATION:INT, GENRE:LONGTEXT, SAMPLERATE:INT, SIZE:INT, TRACK:INT(3), YEAR:INT(4), ALBUM:LONGTEXT, AUDIO_SIZE:INT

# import for external lib hsaudiotag
from hsaudiotag import wma
import sys
import traceback


def process(fullpath, config, rcontext, columns=None):
    try:
        # Gets the WMA file from the path
        myfile = wma.WMADecoder(fullpath)

        # If the wma file can be read succesfully
        if myfile.valid:

            # Store audio data in list
            assorted = [
              myfile.artist,
              myfile.title,
              myfile.channels,
              myfile.comment,
              myfile.duration,
              myfile.genre,
              myfile.sample_rate,
              myfile.size,
              myfile.track,
              myfile.year,
              myfile.album,
              myfile.audio_size]

            # delete the wmaFile variable
            del myfile

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nWMA file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            # Store in database
            return assorted

        else:
            return None

    except:
        traceback.print_exc(file=sys.stderr)

        # Store nothing so the application won't crash
        return None
