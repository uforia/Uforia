'''
Created on 25 apr. 2013

@author: Jimmy van den Berg
'''

import os
import sys


def call_uforia_recursive(config, tmpdir, fullpath):
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
    if config.SPOOFSTARTDIR != None:
        spoofdir = config.SPOOFSTARTDIR + os.path.sep + \
        os.path.relpath(fullpath, config.STARTDIR)
    else:
        spoofdir = fullpath
    new_config.SPOOFSTARTDIR = spoofdir
    new_config.RECURSIVE = True

    uforia.config = new_config
    uforia.run()
    uforia.config = config
