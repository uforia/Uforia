'''
Created on 25 apr. 2013

@author: Jimmy van den Berg
'''

import Uforia_debug
import Uforia
import os

class DummyObject(object):
    pass

def copyConfig(config):
    values = config.__dict__
    newConfig = DummyObject()
    for key, value in values.items():
        if not key.startswith('__'):
            setattr(newConfig, key, value)
    return newConfig

def call_Uforia_recursive(config = None, tmpdir = None, fullpath = None):        
    newConfig = copyConfig(config)
    newConfig.STARTDIR = str(tmpdir)
    newConfig.DROPTABLE = False
    newConfig.TRUNCATE = False
    if config.SPOOFSTARTDIR != None:
        spoofdir = config.SPOOFSTARTDIR + os.path.sep + os.path.relpath(fullpath, config.STARTDIR)
    else:
        spoofdir = fullpath
    newConfig.SPOOFSTARTDIR = spoofdir
    
    Uforia_debug.start(newConfig)