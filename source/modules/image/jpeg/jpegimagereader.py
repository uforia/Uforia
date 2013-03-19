# This is the image module for PNG

#TABLE: jfif:LONGTEXT, adobe:LONGTEXT, progression:LONGTEXT, quality:LONGTEXT, optimize:LONGTEXT, exif:LONGTEXT, jfif_version:LONGTEXT, jfif_density:LONGTEXT, jfif_unit:LONGTEXT, flashpix:LONGTEXT, adobe_transform:LONGTEXT, DPIx:INT, DPIy:INT, XMPtag:LONGTEXT 

import sys, imp
from PIL import Image
from PIL.ExifTags import TAGS
import libxmp

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise

def process(fullpath, columns=None):
        # Try to parse JPG data        
        try:
            #raise
            image = Image.open(fullpath, "r")
            
            assorted = []
            info_dictionary = image.info
            
            # Check if ICC profile is in info dictionary, if so put it in our list
            if "jfif" in info_dictionary:
                assorted.append(info_dictionary["jfif"])
                info_dictionary.pop("jfif")
            else:
                assorted.append(None)
            
            # Check if interlace is in info dictionary, if so put it in our list
            if "adobe" in info_dictionary:
                assorted.append(info_dictionary["adobe"])
                info_dictionary.pop("adobe")
            else:
                assorted.append(None)
            
            # Check if transparency is in info dictionary, if so put it in our list    
            if "progression" in info_dictionary:
                assorted.append(info_dictionary["progression"])
                info_dictionary.pop("progression")
            else:
                assorted.append(None)
            
            # Check if gamma is in info dictionary, if so put it in our list      
            if "quality" in info_dictionary:
                assorted.append(info_dictionary["quality"])
                info_dictionary.pop("quality")
            else:
                assorted.append(None)
            
            # Check if dpi is in info dictionary, if so put it in our list     
            if "optimize" in info_dictionary:
                assorted.append(info_dictionary["optimize"][0])
                info_dictionary.pop("optimize")
            else:
                assorted.append(None)
            
            # Check if aspect is in info dictionary, if so put it in our list                     
            if "exif" in info_dictionary:
                exif = {
                        TAGS[k]: v
                        for k, v in image._getexif().items()
                        if k in TAGS
                        }
                assorted.append(exif)
                info_dictionary.pop("exif")
            else:
                assorted.append(None)
                
            if "jfif_version" in image.info:
                assorted.append(info_dictionary["jfif_version"])
                info_dictionary.pop("jfif_version")
            else:
                assorted.append(None)    
                
            if "jfif_density" in image.info:
                assorted.append(info_dictionary["jfif_density"])
                info_dictionary.pop("jfif_density")
            else:
                assorted.append(None)
                
            if "jfif_unit" in image.info:
                assorted.append(info_dictionary["jfif_unit"])
                info_dictionary.pop("jfif_unit")
            else:
                assorted.append(None)          

            if "flashpix" in image.info:
                assorted.append(info_dictionary["flashpix"])
                info_dictionary.pop("flashpix")
            else:
                assorted.append(None)  

            if "adobe_transform" in image.info:
                assorted.append(info_dictionary["adobe_transform"])
                info_dictionary.pop("adobe_transform")
            else:
                assorted.append(None)                                         
                                      
            if "dpi" in info_dictionary:
                assorted.append(info_dictionary["dpi"][0])
                assorted.append(info_dictionary["dpi"][1])
                info_dictionary.pop("dpi")
            else:
                assorted.append(None)
                assorted.append(None)             
                
            # If there are still other values in the dict then put those in column
#            assorted.append(info_dictionary)
            
            # Delete variable
            del info_dictionary, image
            
            # Store the embedded XMP metadata
            xmpfile = libxmp.XMPFiles(file_path=fullpath)
            assorted.append(str(xmpfile.get_xmp()))
            xmpfile.close_file()
                
            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)
            
            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nJPEG file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i]+':', assorted[i])
                print

            return assorted
            
        except:
            print "An error occured while parsing image data: ", sys.exc_info()
        
            # Store values in database so not the whole application crashes
            return None
    
# 
#def get_exif(fn):
#    ret = {}
#    i = Image.open(fn)
#    info = i._getexif()
#    for tag, value in info.items():
#        decoded = TAGS.get(tag, tag)
#        ret[decoded] = value
#    return ret