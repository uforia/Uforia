'''
Created on 16 apr. 2013

@author: marcin
'''

# Generic video module using avbin (which is a stable API for libav, a
# fork of the widely used ffmpeg library)

#TABLE: structure_size:INT, n_streams:INT, start_time:BIGINT, duration:BIGINT, title:LONGTEXT, author:LONGTEXT, copyright:LONGTEXT, comment:LONGTEXT, album:LONGTEXT, year:INT, track:INT, genre:LONGTEXT

import sys, traceback
import ctypes

class AVbinFileInfo(ctypes.Structure):
    _fields_ = [
        ('structure_size', ctypes.c_size_t),
        ('n_streams', ctypes.c_int),
        ('start_time', ctypes.c_int64),
        ('duration', ctypes.c_int64),
        ('title', ctypes.c_char * 512),
        ('author', ctypes.c_char * 512),
        ('copyright', ctypes.c_char * 512),
        ('comment', ctypes.c_char * 512),
        ('album', ctypes.c_char * 512),
        ('year', ctypes.c_int),
        ('track', ctypes.c_int),
        ('genre', ctypes.c_char * 32),
    ]

av = ctypes.cdll.LoadLibrary('avbin')
av.avbin_open_filename.restype = ctypes.c_void_p
av.avbin_open_filename.argtypes = [ctypes.c_char_p]
av.avbin_file_info.restype = ctypes.c_int
av.avbin_file_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(AVbinFileInfo)]
av.avbin_init()

def process(fullpath, config, columns=None):
        try:
            file_info = AVbinFileInfo()
            file_info.structure_size = ctypes.sizeof(file_info)
            file = av.avbin_open_filename(fullpath)
            av.avbin_file_info(file, ctypes.byref(file_info))

            assorted = []
            for field in file_info._fields_:
                assorted.append(getattr(file_info, field[0]))

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nPNG file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i], assorted[i])
                print

            return assorted

        except:
            traceback.print_exc(file = sys.stderr)
            return None