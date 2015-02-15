#!/usr/bin/env python

# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the audio module for .ogg

# TABLE: artist:LONGTEXT, album:LONGTEXT, title:LONGTEXT, genre:LONGTEXT, year:INT(4), track:INT, comment:LONGTEXT, duration_in_seconds:DOUBLE, bitrate:INT, samplerate:INT, audio_filesize:INT, audio_offset:INT

import sys
import traceback
from hsaudiotag import auto


def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath
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
