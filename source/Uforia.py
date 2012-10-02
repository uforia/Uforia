#!/usr/bin/env python

# Load basic Python modules
import os, sys, re, time, multiprocessing
sys.path.append('./include')

# Load Uforia custom modules
import config, File, magic, modscanner
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")

from Uforia.models import * 
from Uforia.modules.models import *

class Uforia(object):
    def __init__(self):
        print "Setting up "+str(config.CONSUMERS)+" consumer(s)..."
        self.consumers = multiprocessing.Pool(processes=config.CONSUMERS)
        if config.DEBUG:
            print "Starting producer..."
        self.fileScanner(config.STARTDIR)

    def fileScanner(self,dir):
        if config.DEBUG:
            print "Starting in directory "+config.STARTDIR+"..."
            print "Starting Filepath Scanner..."
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath=os.path.join(root,name)
                self.consumers.apply_async(self.fileProcessor(fullpath))
                if config.DEBUG:
                    print "Added:",fullpath
        return
    
    def fileProcessor(self,fullpath):
        self.file = File.File(fullpath,config.DEBUG)
        try:
	        hash.save()
	        if config.DEBUG:
	            print "Hashes and metadata exported to database."
	        metadata = Metadata(Location = self.file.fullpath, Name = self.file.name, MTimes = self.file.mtime, ATimes = self.file.atime, CTimes = self.file.ctime, Owner = self.file.owner, Groups = self.file.group, Permissions = '?')
	        metadata.save()
        except:
            if not config.DEBUG:
                raise IOError('Error storing hashes, possible database problem.')
    
        xmtype = ''.join(e for e in self.file.mtype if e.isalnum())
        if config.DEBUG:
            print "\n","Clean Filetype: ", xmtype
        externalresult = xmtype
        try:
            result = modscanner.modname.index(externalresult)
            rt = result + 1
            resulttest = modscanner.modname[rt]
            er = "modules/"
            er += externalresult
            if externalresult in resulttest:
                filelauncher = resulttest
                filelauncher += " "
                filelauncher += filepath
                os.system(filelauncher)
        except:
            pass
        return
					
if __name__ == "__main__":
    modscanner.findmods(modscanner.modtop)
    main = Uforia()
