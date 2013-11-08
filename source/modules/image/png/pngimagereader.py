# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the image module for PNG

# TABLE: tile:LONGTEXT, text:LONGTEXT, icc_profile:BLOB, interlace:INT, transparency:LONGTEXT, gamma:INT, dpi_x:INT, dpi_y:INT, aspect:LONGTEXT, other_info:LONGTEXT, XMP:LONGTEXT

import sys
import traceback
from PIL import Image


def process(fullpath, config, rcontext, columns=None):

        # Try to parse PNG data
        try:
            image = Image.open(fullpath, "r")

            assorted = [image.tile, image.text]
            info_dictionary = image.info

            # Check if ICC profile is in info dictionary
            # if so put it in our list
            if "icc_profile" in info_dictionary:
                assorted.append(info_dictionary["icc_profile"])
                info_dictionary.pop("icc_profile")
            else:
                assorted.append(None)

            # Check if interlace is in info dictionary
            # if so put it in our list
            if "interlace" in info_dictionary:
                assorted.append(info_dictionary["interlace"])
                info_dictionary.pop("interlace")
            else:
                assorted.append(None)

            # Check if transparency is in info dictionary
            # if so put it in our list
            if "transparency" in info_dictionary:
                assorted.append(info_dictionary["transparency"])
                info_dictionary.pop("transparency")
            else:
                assorted.append(None)

            # Check if gamma is in info dictionary, if so put it in our list
            if "gamma" in info_dictionary:
                assorted.append(info_dictionary["gamma"])
                info_dictionary.pop("gamma")
            else:
                assorted.append(None)

            # Check if dpi is in info dictionary, if so put it in our list
            if "dpi" in info_dictionary:
                assorted.append(info_dictionary["dpi"][0])
                assorted.append(info_dictionary["dpi"][1])
                info_dictionary.pop("dpi")
            else:
                assorted.append(None)
                assorted.append(None)

            # Check if aspect is in info dictionary, if so put it in our list
            if "aspect" in image.info:
                assorted.append(info_dictionary["aspect"])
                info_dictionary.pop("aspect")
            else:
                assorted.append(None)

            # If there are still other values in the dict
            # then put those in column
            assorted.append(info_dictionary)

            # Delete variable
            del info_dictionary, image

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
                print "\nPNG file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
