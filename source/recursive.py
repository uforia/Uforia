'''
Created on 25 apr. 2013

@author: Jimmy van den Berg
'''

import os
import sys


def call_Uforia_recursive(config, tmpdir, fullpath):
    """
    Call Uforia recursively on the specified temporary directory.
    config - The Uforia config object
    tmpdir - The temporary directory to be used as STARTDIR
    fullpath - The full path to the image/archive which shall be used
        as prefix in the output columns
    """
    if config.UFORIA_RUNNING_VERSION == 'Uforia_debug':
        import Uforia_debug
        uforia = Uforia_debug
    else:
        import Uforia
        uforia = Uforia

    newConfig = uforia.configAsPickleable(config)
    newConfig.STARTDIR = str(tmpdir)
    newConfig.DROPTABLE = False
    newConfig.TRUNCATE = False
    if config.SPOOFSTARTDIR != None:
        spoofdir = config.SPOOFSTARTDIR + os.path.sep + \
        os.path.relpath(fullpath, config.STARTDIR)
    else:
        spoofdir = fullpath
    newConfig.SPOOFSTARTDIR = spoofdir
    newConfig.RECURSIVE = True

    uforia.config = newConfig
    uforia.run()
    uforia.config = config
