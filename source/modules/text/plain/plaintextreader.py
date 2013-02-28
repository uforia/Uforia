'''
Created on 02 feb. 2013

@author: Arnim Eijkhoudt
'''

#!/usr/bin/env python

# This is the plain text module for .txt

#TABLE: Contents:LONGTEXT

import sys, imp

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
except:
    raise

def process(fullpath):
        # Try to parse TXT data
        try:
            with open(fullpath,'rb') as f:
                values=f.read()
            
            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nTXT file data:"
                print "Contents:    %s" % values
                print
            
            return (values,)
            
        except:
            print "An error occured while parsing audio data: ", sys.exc_info()
        
            # Store values in database so not the whole application crashes
            return (None, )