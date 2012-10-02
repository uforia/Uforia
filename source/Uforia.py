#!/usr/bin/env python

# Load basic Python modules
import os, sys, re, time, multiprocessing
sys.path.append('./include')

# Load Uforia custom modules
import config, File, magic
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")

from Uforia.models import * 
from Uforia.modules.models import *

class Uforia(object):
    def __init__(self):
        print "Listing available modules for MIME types..."
        self.moduleScanner()
        print "Setting up "+str(config.CONSUMERS)+" consumer(s)..."
        self.consumers = multiprocessing.Pool(processes=config.CONSUMERS)
        if config.DEBUG:
            print "Starting producer..."
        self.fileScanner(config.STARTDIR)

    def moduleScanner(self):
        if config.DEBUG:
            print "Starting in directory "+config.MODULES+"..."
            print "Starting modulescanner..."
        self.modules={}
        for major in os.listdir(config.MODULES):
            for minor in os.listdir(config.MODULES+major):
                mimetype=major+'/'+minor
                self.modules[mimetype]=os.listdir(config.MODULES+mimetype)
        if config.DEBUG:
            print "Supported modules: "
            for mimetype in self.modules:
                print "Mimetype: "+mimetype+"\tList of handlers:",self.modules[mimetype]


    def fileScanner(self,dir):
        if config.DEBUG:
            print "Starting in directory "+config.STARTDIR+"..."
            print "Starting filescanner..."
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath=os.path.join(root,name)
                self.consumers.apply_async(self.fileProcessor(fullpath))
                if config.DEBUG:
                    print "Added:",fullpath
    
    def fileProcessor(self,fullpath):
        self.file = File.File(fullpath,config.DEBUG)
        try:
	        if config.DEBUG:
	            print "Hashes and metadata exported to database."
	        # TODO: Store the stuff in the database
        except:
            raise IOError('Error storing hashes, possible database problem.')
					
if __name__ == "__main__":
    main = Uforia()
