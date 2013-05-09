'''
Created on 25 apr. 2013

@author: Jimmy van den Berg
'''

import os
import sys
import copy

class RecursionContext:
    """
    A set of configuration attributes needed for running Uforia
    recursively that should not be modifiable by the user. 
    """
    def __init__(self):
        # Can be used to fake the path of STARTDIR in the database
        # output.
        self.SPOOFSTARTDIR = None

        # Used to change the starting value of the hash id if Uforia was 
        # called recursively
        self.STARTING_HASHID = 1

        # Used to notify that Uforia was started recursively
        self.RECURSIVE = False

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

    new_rcontext = copy.copy(rcontext)
    if new_rcontext.SPOOFSTARTDIR != None:
        spoofdir = new_rcontext.SPOOFSTARTDIR + os.path.sep + \
        os.path.relpath(fullpath, config.STARTDIR)
    else:
        spoofdir = fullpath
    new_rcontext.SPOOFSTARTDIR = spoofdir
    new_rcontext.RECURSIVE = True

    uforia.config = new_config
    uforia.rcontext = new_rcontext
    uforia.run()
    uforia.config = config
    rcontext.STARTING_HASHID = new_rcontext.STARTING_HASHID
    uforia.rcontext = rcontext
