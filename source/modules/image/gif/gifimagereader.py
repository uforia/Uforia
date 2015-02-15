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

# This is the image module for GIF

# TABLE: version:LONGTEXT, duration:BIGINT, transparancy_color:SMALLINT, background_color:SMALLINT, frames:INT, loop:SMALLINT, application_extension:LONGTEXT, XMP:LONGTEXT

import sys
import traceback
from PIL import Image

def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    # Try to parse the GIF data
    try:
        image = Image.open(fullpath, "r")

        assorted = [
            image.info['version'],
            image.info['duration'],
            image.info['transparency'],
            image.info['background'],
        ]

        # Seek until EOF to find the number of animation frames
        noframes = 0
        try:
            while True:
                noframes += 1
                image.seek(image.tell() + 1)
        except EOFError:
            pass
        assorted.append(noframes)

        if 'loop' in image.info:
            assorted.append(image.info['loop'])
        else:
            assorted.append(0)

        if 'extension' in image.info:
            assorted.append(image.info['extension'])
        else:
            assorted.append(None)

        # Close the PIL image handler
        del image

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
            print "\nGIF file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file=sys.stderr)
        return None
