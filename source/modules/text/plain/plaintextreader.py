'''
Created on 02 feb. 2013

@author: Arnim Eijkhoudt
'''

#!/usr/bin/env python

# This is the plain text module for .txt

#TABLE: Contents:LONGTEXT

import sys, traceback

def process(fullpath, config, columns=None):
        # Try to parse TXT data
        try:
            with open(fullpath,'rb') as f:
                assorted = [f.read()]
            
                # Make sure we stored exactly the same amount of columns as
                # specified!!
                assert len(assorted) == len(columns)
        
                # Print some data that is stored in the database if debug is true
                if config.DEBUG:
                    print "\nTXT file data:"
                    for i in range(0, len(assorted)):
                        print "%-18s %s" % (columns[i], assorted[i])
                        print

                return assorted            
        except:
            traceback.print_exc(file = sys.stderr)
        
            # Store values in database so not the whole application crashes
            return (None, )