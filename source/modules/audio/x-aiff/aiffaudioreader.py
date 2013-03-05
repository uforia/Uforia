'''
Created on 2 mrt. 2013

@author: Jimmy van den Berg
'''

#!/usr/bin/env python

# This is the audio module for .aiff(c)

#TABLE: NumberOfChannels:INT(3), SampleWidth:INT(3), FrameRate:INT(6), NumberOfFrames:INT(6), DurationInSeconds:FLOAT, CompressionType:LONGTEXT, CompressionName:LONGTEXT

import sys, imp
import aifc

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise

def process(fullpath, columns=None):
        # Try to parse AIFF data
        try:
            # Open the AIFF file
            audiofile = aifc.open(fullpath, "rb")
            
            #fill variables from the AIFF file        
            (nchannels, sampwidth, framerate, nframes, comptype, compname) = audiofile.getparams()
            
            # duration of the wave file is amount of frames divided by framerate
            duration = nframes / float(framerate) 
            
            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nAIFF file data:"
                print "NumberOfChannels: %s" % str(nchannels)
                print "SampleWidth:      %s" % str(sampwidth)
                print "FrameRate:        %s" % str(framerate)
                print "NumberOfFrames:   %s" % str(nframes)
                print "Duration:         %s" % str(duration)
                print "CompressionType:  %s" % comptype
                print "CompressionName:  %s" % compname
                print
            
            # Return all info from the audio file    
            return(nchannels, sampwidth, framerate, nframes, duration, comptype, compname,)
            
        except:
            print "An error occured while parsing audio data: ", sys.exc_info()
        
            # Store values in database so not the whole application crashes
            return None       