'''
Created on 2 mrt. 2013

@author: Jimmy van den Berg
'''

# This is the audio module for .aiff(c)

# TABLE: NumberOfChannels:INT, SampleWidth:INT, FrameRate:INT, NumberOfFrames:INT, CompressionType:LONGTEXT, CompressionName:LONGTEXT, DurationInSeconds:DOUBLE

import sys
import traceback
import aifc


def process(fullpath, config, columns=None):
        # Try to parse AIFF data
        try:
            # Open the AIFF file
            audiofile = aifc.open(fullpath, "rb")

            # fill variables from the AIFF file (nchannels,
            # sampwidth, framerate, nframes, comptype, compname)
            assorted = list(audiofile.getparams())

            # duration of the aiff file is amount of frames
            # divided by framerate
            assorted.append(audiofile.getnframes()
                            / float(audiofile.getframerate()))

            # close the aiffFile
            audiofile.close()

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nAIFF file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
