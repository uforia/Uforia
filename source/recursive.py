'''
Created on 25 apr. 2013

@author: Jimmy van den Berg
'''

import os
import sys
import copy
import multiprocessing

class RecursionContext:
    """
    A set of configuration attributes needed for running Uforia
    recursively that should not be modifiable by the user. 
    """
    def __init__(self):
        # Can be used to fake the path of STARTDIR in the database
        # output.
        self.spoofed_startdir = None

        # Used to change the starting value of the hash id if Uforia was 
        # called recursively
        self.hashid = multiprocessing.Value('i', 1)

        # Lock for changing the HASHID
        self.hashid_lock = multiprocessing.Lock()

        # Used to notify that Uforia was started recursively
        self.is_recursive = False

def call_uforia_recursive(config, rcontext, tmpdir, fullpath):
    """
    Call Uforia recursively on the specified temporary directory.
    config - The Uforia config object
    tmpdir - The temporary directory to be used as STARTDIR
    fullpath - The full path to the image/archive which shall be used
        as prefix in the output columns
    """
    if config.UFORIA_RUNNING_VERSION == 'Uforia_debug':
        import uforia_debug
        uforia = uforia_debug
    else:
        import uforia
        uforia = uforia

    new_config = uforia.config_as_pickleable(config)
    new_config.STARTDIR = str(tmpdir)
    new_config.DROPTABLE = False
    new_config.TRUNCATE = False

    new_rcontext = RecursionContext()
    if rcontext.spoofed_startdir != None:
        spoofdir = rcontext.spoofed_startdir + os.path.sep + \
        os.path.relpath(fullpath, config.STARTDIR)
    else:
        spoofdir = fullpath
    new_rcontext.spoofed_startdir = spoofdir
    new_rcontext.hashid = rcontext.hashid
    new_rcontext.hashid_lock = rcontext.hashid_lock
    new_rcontext.is_recursive = True

    uforia.config = new_config
    uforia.rcontext = new_rcontext
    uforia.run()
    uforia.config = config
    uforia.rcontext = rcontext
