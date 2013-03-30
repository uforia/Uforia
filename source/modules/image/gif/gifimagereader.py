'''
Created on 25 mrt. 2013

@author: Marcin Koziuk
'''

# This is the image module for GIF

#TABLE: Version:LONGTEXT, Duration:BIGINT, TransparancyColour:SMALLINT, BackgroundColour:SMALLINT, Frames:INT, Loop:SMALLINT, ApplicationExtension:BLOB, XMP:BLOB
import sys, traceback
from PIL import Image

def process(fullpath, config, columns=None):
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
                image.seek(image.tell()+1)
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
        traceback.print_exc(file = sys.stderr)
        return None