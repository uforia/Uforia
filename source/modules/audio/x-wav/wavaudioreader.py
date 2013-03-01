'''
Created on 21 feb. 2013

@author: Jimmy van den Berg
'''
#!/usr/bin/env python

# This is the audio module for wav files

#TABLE: NumberOfChannels:INT(3), SampleWidth:INT(3), FrameRate:INT(6), NumberOfFrames:INT(6), DurationInSeconds:FLOAT, CompressionType:LONGTEXT, CompressionName:LONGTEXT

import sys, imp;
import struct;
import wave;

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise

def process(fullpath, columns=None):
    try:
        #open the wave file
        waveFile = wave.open(fullpath, "rb")
        
        #fill variables from the wave file        
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = waveFile.getparams()

        # duration of the wave file is amount of frames divided by framerate
        duration = nframes / float(framerate) 
        
        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nWAV file data:"
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
        print "An error occured while parsing wav data: ", sys.exc_info()
        
        # Store values in database so not the whole application crashes
        return(None, None, None, None, None, None, None, None, None)