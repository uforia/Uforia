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
        waveFile = wave.open(fullpath, "rb") #open de wave file
        
        (nchannels, sampwidth, framerate, nframes, comptype, compname) = waveFile.getparams() #vul de variabelen met de parameters van de wave file          
        frames = waveFile.readframes(nframes * nchannels)   # aantal frames keer het aantal channels worden gelezen             
        out = struct.unpack_from ("%dh" % nframes * nchannels, frames)

        duration = nframes / float(framerate) # duur van de wave file is aantal frames keer framerate

       # Convert 2 channels to arrays
        if nchannels == 2: # als er 2 channels zijn bestaan de linker en rechter box
           left_audio_stream = out[0::2]
           right_audio_stream = out[1::2]           
        else: # als er geen 2 zijn komt er alleen uit de linker kant geluid
            left_audio_stream = array(out)
            right_audio_stream = None  
            
        return(nchannels, sampwidth, framerate, nframes, duration, comptype, compname,)
    except:
        print "An error occured while parsing wav data: ", sys.exc_info()
        return(None, None, None, None, None, None, None, None, None)