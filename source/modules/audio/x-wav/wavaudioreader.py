'''
Created on 21 feb. 2013

@author: Jimmy van den Berg
'''
#!/usr/bin/env python

# This is the audio module for wav files

#TABLE: NumberOfChannels:INT(3), SampleWidth:INT(3), FrameRate:INT(6), NumberOfFrames:INT(6), DurationInSeconds:FLOAT, CompressionType:LONGTEXT, CompressionName:LONGTEXT, XMP:LONGTEXT

import sys, imp
import struct
import wave
import libxmp

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

        # close the wavefile first before opening using the XMP toolkit
        waveFile.close()

        # Store the embedded XMP metadata
        xmpfile = libxmp.XMPFiles(file_path=fullpath)
        xmp = str(xmpfile.get_xmp())
        xmpfile.close_file()
        
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
        return(nchannels, sampwidth, framerate, nframes, duration, comptype, compname, xmp)
    
    except:
        print "An error occured while parsing wav data: ", sys.exc_info()
        
        return None