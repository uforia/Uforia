'''
Created on 21 feb. 2013

@author: Jimmy van den Berg
'''
#!/usr/bin/env python

# This is the audio module for wav files

#TABLE: NumberOfChannels:INT(3), SampleWidth:INT(3), FrameRate:INT(6), NumberOfFrames:INT(6), DurationInSeconds:FLOAT, CompressionType:LONGTEXT, CompressionName:LONGTEXT

import sys;
import struct;
import wave;

def process(fullpath):
    try:
        waveFile = wave.open(fullpath, "rb") #open the wave file
        
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = waveFile.getparams() #fill variables from the wave file        

        duration = nframes / float(framerate) # duration of the wave file is amount of frames divided by framerate
            
        # Return all info from the audio file    
        return(nchannels, sampwidth, framerate, nframes, duration, comptype, compname,)
    except:
        print "An error occured while parsing wav data: ", sys.exc_info()
        
        # Store values in database so not the whole application crashes
        return(None, None, None, None, None, None, None, None, None)