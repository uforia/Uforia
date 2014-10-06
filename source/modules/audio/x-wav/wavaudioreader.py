# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the audio module for wav files

# TABLE: number_of_channels:INT, sample_width:INT, framerate:INT, number_of_frames:INT, compression_type:LONGTEXT, compression_name:LONGTEXT, duration_in_seconds:DOUBLE, XMP:LONGTEXT

import sys
import traceback
import wave


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    try:
        # open the wave file
        wave_file = wave.open(fullpath, "rb")

        # fill variables from the wave file, (nchannels, sampwidth,
        # framerate, nframes, comptype, compname)
        assorted = list(wave_file.getparams())

        # duration of the wave file is amount of frames divided by framerate
        assorted.append(wave_file.getnframes() / float(wave_file.getframerate()))

        # close the wavefile first before opening using the XMP toolkit
        wave_file.close()

        # Store the embedded XMP metadata
        if config.ENABLEXMP:
            import libxmp
            xmpfile = libxmp.XMPFiles(file_path=fullpath)
            assorted.append(str(xmpfile.get_xmp()))
            xmpfile.close_file()
        else:
            assorted.append(None)

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nWAV file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)

        return None
