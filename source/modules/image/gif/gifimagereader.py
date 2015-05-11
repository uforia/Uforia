#!/usr/bin/env python

# Copyright (C) 2013-2015 A. Eijkhoudt and others

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the image module for GIF

# TABLE: version:LONGTEXT, duration:BIGINT, transparency:SMALLINT, background:SMALLINT, frames:INT, loop:SMALLINT, application_extension:LONGTEXT, XMP:LONGTEXT

import sys
import traceback
from PIL import Image

def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    # Try to parse the GIF data
    try:
        assorted = []
        image = Image.open(fullpath, "r")
        if 'version' in image.info:
            assorted.append(image.info['version'])
        else:
            assorted.append(0)
        if 'duration' in image.info:
            assorted.append(image.info['duration'])
        else:
            assorted.append(0)
        if 'transparency' in image.info:
            assorted.append(image.info['transparency'])
        else:
            assorted.append(0)
        if 'background' in image.info:
            assorted.append(image.info['background'])
        else:
            assorted.append(0)

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
            if xmpfile.get_xmp():
                assorted.append(str(xmpfile.get_xmp()))
            else:
                assorted.append(None)
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
