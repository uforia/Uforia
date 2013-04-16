'''
Created on 21 feb. 2013

@author: Jimmy van den Berg
'''

# This is the audio module for wav files

#TABLE: NumberOfChannels:INT, SampleWidth:INT, FrameRate:INT, NumberOfFrames:INT, CompressionType:LONGTEXT, CompressionName:LONGTEXT, DurationInSeconds:DOUBLE, XMP:LONGTEXT

import sys, traceback
import wave

def process(fullpath, config, columns=None):
    try:
        #open the wave file
        waveFile = wave.open(fullpath, "rb")

        #fill variables from the wave file, (nchannels, sampwidth, framerate, nframes, comptype, compname)
        assorted = list(waveFile.getparams())

        # duration of the wave file is amount of frames divided by framerate
        assorted.append(waveFile.getnframes() / float(waveFile.getframerate()))

        # close the wavefile first before opening using the XMP toolkit
        waveFile.close()

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
            print "\nWAV file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file = sys.stderr)

        return None
