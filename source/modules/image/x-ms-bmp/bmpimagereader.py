# This is the image module for BMP

#TABLE: Tile:LONGTEXT, Compression:LONGTEXT, Remaining:LONGTEXT

import sys, imp, traceback
from PIL import Image
from PIL.ExifTags import TAGS

def process(fullpath, config, columns=None):
    # Try to parse BMP data
    try:
        image = Image.open(fullpath, "r")
        
        assorted = [image.tile, ]
        info_dictionary = image.info
                        
        # Check if compression is in info dictionary, if so put it in our list
        if "compression" in info_dictionary:
            assorted.append(info_dictionary["compression"])
            info_dictionary.pop("compression")
        else:
            assorted.append(None)
            
        # If there are still other values in the dict then put those in column
        assorted.append(info_dictionary)
               
        # Delete variable
        del info_dictionary, image
        
        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)
        
        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nBMP file data:"
            for i in range(0, len(assorted)):
                print "%-18s; %s" % (columns[i], assorted[i])
            print

        return assorted
        
    except:
        traceback.print_exc(file = sys.stderr)
    
        # Store values in database so not the whole application crashes
        return None