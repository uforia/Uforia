'''
Created on 13 mei 2013

@author: marcin
'''
# Module for extracting .gz files and running uforia over the extracted
# file

# TABLE: offset:INT, extrabuf:LONGTEXT, extrasize:INT, extrastart:INT

import sys
import traceback
import tempfile
import shutil
import gzip
import os
import recursive


def _uncompressed_filename(fullpath):
    """
    Returns the filename for the ungzipped file. Examples:
    test.txt.gz => test.txt
    test.tgz => test.tar
    test => test~ungzipped
    """
    lastpart = os.path.relpath(fullpath, os.path.dirname(fullpath))
    if lastpart.endswith(".gz"):
        return lastpart[:-3]
    elif lastpart.endswith(".tgz"):
        return lastpart[:-4] + ".tar"
    else:
        return lastpart + "~ungzipped"


def process(fullpath, config, rcontext, columns=None):
    try:
         # Create a temporary directory
        tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

        # Open gzip file for reading
        file = gzip.open(fullpath, 'rb')

        # Store gzip metadata values
        assorted = [file.offset,
                    file.extrabuf,
                    file.extrasize,
                    file.extrastart]

        # Read the uncompressed data
        file_content = file.read()

        # Write it to the temp folder
        uncompressed_file = open(tmpdir + os.path.sep
                                 + _uncompressed_filename(fullpath),
                                 "wb")

        uncompressed_file.write(file_content)

        # Close both files
        uncompressed_file.close()
        file.close()

        # Call Uforia recursively
        recursive.call_uforia_recursive(config, rcontext, tmpdir,
                                        os.path.dirname(fullpath))

        # Delete the temporary directory, proceed even if it causes
        # an error
        try:
            shutil.rmtree(tmpdir)
        except:
            traceback.print_exc(file=sys.stderr)

        return assorted
    except:
        traceback.print_exc(file=sys.stderr)
    return None
