'''
Created on 11 mrt. 2013

@author: Jimmy van den Berg
'''

# This is the image module reading all images

#TABLE: Format:LONGTEXT, Mode:LONGTEXT, Width:INT, Height:INT, Colors:LONGTEXT, Extrema:LONGTEXT, Palette:LONGTEXT

import sys, imp
from PIL import Image

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise

def process(fullpath, columns=None):
        # Try to parse image data
        try:
            #Open image file
            image = Image.open(fullpath, "r")
            
            assorted = [image.format, image.mode, image.size[0], image.size[1], image.getcolors(), image.getextrema(), image.palette]            

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)
            
            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nImage file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i]+':', assorted[i])
                print
            
            return assorted
            
        except:
            print "An error occured while parsing image data: ", sys.exc_info()
        
            # Store values in database so not the whole application crashes
            return None