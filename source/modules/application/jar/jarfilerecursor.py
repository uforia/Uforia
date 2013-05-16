'''
Created on 15 mei 2013

@author: Jimmy van den Berg
'''

# Stores the jar file metadata and starts Uforia recursively on the
# files inside the jar folder.

# TABLE: file_names:LONGTEXT, total_files:INT, zip_stored:INT, zip_deflated:INT, debug:LONGTEXT, comment:LONGTEXT, contentInfo:LONGTEXT

import sys
import traceback
import imp


def process(fullpath, config, rcontext, columns=None):
        # Try to parse jar data
        try:
            # Get instance of zip module
            zip_module = imp.load_source('zipfilerecursor',
                                         'modules/application/' +
                                         'zip/zipfilerecursor.py')

            # JAR files works the same as ZIP files so let the ZIP module
            # handle the file.
            assorted = zip_module.process(fullpath, config, rcontext, columns)

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
