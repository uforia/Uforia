# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the image module for TIFF

# TABLE: tile:LONGTEXT, icc_profile:BLOB, compression:LONGTEXT, dpi_x:INT, dpi_y:INT, resolution_x:INT, resolution_y:INT, other_info:LONGTEXT, bits_per_sample:LONGTEXT, photo_metric:LONGTEXT, file_order:LONGTEXT, image_description:LONGTEXT, strip_offsets:BLOB, samples_per_pixel:LONGTEXT, rows_per_strip:LONGTEXT, strip_byte_counts:BLOB, x_resolution:INT, y_resolution:INT, planar_config:LONGTEXT, resolution_unit:LONGTEXT, software:LONGTEXT, datetime:TEXT, artist:LONGTEXT, predictor:LONGTEXT, colormap:LONGTEXT, tileoffsets:BLOB, extrasamples:LONGTEXT, sampleformat:LONGTEXT, jpeg_tables:LONGTEXT, copyright:LONGTEXT, iptcnaa_chunk:LONGTEXT, photoshop_chunck:LONGTEXT, exif_ifd:LONGTEXT, XMP:LONGTEXT

import sys
import traceback
import python_dateutil as dateutil
from PIL import Image, TiffImagePlugin


def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath

        # Try to parse TIFF data
        try:
            image = Image.open(fullpath, "r")

            assorted = [image.tile]
            info_dictionary = image.info

            # Check if ICC profile is in info dictionary,
            # if so put it in our list
            if "icc_profile" in info_dictionary:
                assorted.append(info_dictionary["icc_profile"])
                info_dictionary.pop("icc_profile")
            else:
                assorted.append(None)

            # Check if compression is in info dictionary,
            # if so put it in our list
            if "compression" in info_dictionary:
                assorted.append(info_dictionary["compression"])
                info_dictionary.pop("compression")
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

            # Check if resolution is in info dictionary,
            # if so put it in our list
            if "resolution" in info_dictionary:
                assorted.append(info_dictionary["resolution"][0])
                assorted.append(info_dictionary["resolution"][1])
                info_dictionary.pop("resolution")
            else:
                assorted.append(None)
                assorted.append(None)

            # If there are still other values in the
            # dict then put those in column
            assorted.append(info_dictionary)

            # Get all values from tag atribute, EXIF Tags
            assorted.append(image.tag.get(TiffImagePlugin.BITSPERSAMPLE))
            assorted.append(image.tag.get
                            (TiffImagePlugin.PHOTOMETRIC_INTERPRETATION))
            assorted.append(image.tag.get(TiffImagePlugin.FILLORDER))
            assorted.append(image.tag.get(TiffImagePlugin.IMAGEDESCRIPTION))
            assorted.append(image.tag.get(TiffImagePlugin.STRIPOFFSETS))
            assorted.append(image.tag.get(TiffImagePlugin.SAMPLESPERPIXEL))
            assorted.append(image.tag.get(TiffImagePlugin.ROWSPERSTRIP))
            assorted.append(image.tag.get(TiffImagePlugin.STRIPBYTECOUNTS))
            assorted.append(image.tag.get(TiffImagePlugin.X_RESOLUTION))
            assorted.append(image.tag.get(TiffImagePlugin.Y_RESOLUTION))
            assorted.append(image.tag.get
                            (TiffImagePlugin.PLANAR_CONFIGURATION))
            assorted.append(image.tag.get(TiffImagePlugin.RESOLUTION_UNIT))
            assorted.append(image.tag.get(TiffImagePlugin.SOFTWARE))
            assorted.append(image.tag.get(TiffImagePlugin.DATE_TIME))
            assorted.append(image.tag.get(TiffImagePlugin.ARTIST))
            assorted.append(image.tag.get(TiffImagePlugin.PREDICTOR))
            assorted.append(image.tag.get(TiffImagePlugin.COLORMAP))
            assorted.append(image.tag.get(TiffImagePlugin.TILEOFFSETS))
            assorted.append(image.tag.get(TiffImagePlugin.EXTRASAMPLES))
            assorted.append(image.tag.get(TiffImagePlugin.SAMPLEFORMAT))
            assorted.append(image.tag.get(TiffImagePlugin.JPEGTABLES))
            assorted.append(image.tag.get(TiffImagePlugin.COPYRIGHT))
            assorted.append(image.tag.get(TiffImagePlugin.IPTC_NAA_CHUNK))
            assorted.append(image.tag.get(TiffImagePlugin.PHOTOSHOP_CHUNK))
            assorted.append(image.tag.get(TiffImagePlugin.EXIFIFD))

            # Delete variable
            del image, info_dictionary

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

            # Fix date format
            index = columns.index('datetime')
            if assorted[index] is not None:
                assorted[index] = dateutil.parser.parse(assorted[index]).isoformat()

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nTiff file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
