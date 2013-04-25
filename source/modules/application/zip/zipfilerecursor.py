'''
Created on 24 apr. 2013

@author: marcin
'''

import recursive;

# Stores the zip file metadata and starts Uforia recursively on the
# files inside the zip folder.

#TABLE: test:LONGTEXT

import sys, traceback, os, tempfile, shutil, copy
import zipfile

def process(fullpath, config, columns=None):
    try:
        assorted = [ "test" ]

        # Create a temporary directory
        tmpdir = tempfile.mkdtemp("_uforiatmp")

        # Extract the zip file
        zip = zipfile.ZipFile(fullpath, mode = 'r')
        zip.extractall(tmpdir)
        
        recursive.call_Uforia_recursive(config, tmpdir, fullpath);
        
        # Close the zip file
        zip.close()

        # Delete the temporary directory, proceed even if it causes
        # an error
        try:
            pass
            shutil.rmtree(tmpdir)
        except:
            traceback.print_exc(file = sys.stderr)

        # Make sure we stored exactly the same amount of columns as
        # specified!!
        assert len(assorted) == len(columns)

        # Print some data that is stored in the database if debug is true
        if config.DEBUG:
            print "\nZip file data:"
            for i in range(0, len(assorted)):
                print "%-18s %s" % (columns[i], assorted[i])
            print

        return assorted

    except:
        traceback.print_exc(file = sys.stderr)
        return None
