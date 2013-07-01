# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the image module reading all images

# TABLE: Format:LONGTEXT, Mode:LONGTEXT, Width:INT, Height:INT, Colors:LONGTEXT, Extrema:LONGTEXT, Histogram:LONGTEXT, Palette:LONGTEXT, LeftBoundingbox:INT, UpperBoundingbox:INT, RightBoundingbox:INT, LowerBoundingbox:INT

import sys
import traceback
from PIL import Image


def process(fullpath, config, rcontext, columns=None):
        # Try to parse image data
        try:
            # Open image file
            image = Image.open(fullpath, "r")

            assorted = [image.format, image.mode,
                        image.size[0], image.size[1],
                        image.getcolors(), image.getextrema(),
                        image.histogram()]

            # If palette is not None get it's data
            if image.palette == None:
                assorted.append(None)
            else:
                assorted.append(image.palette.getdata())

            #
            if image.getbbox() == None:
                assorted.append(None)
            else:
                assorted.append(image.getbbox()[0])
                assorted.append(image.getbbox()[1])
                assorted.append(image.getbbox()[2])
                assorted.append(image.getbbox()[3])

            # Delete variable
            del image

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nImage file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
