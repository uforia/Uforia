#!/usr/bin/env python

"""
All 'print' lines are used for debug purposes
"""

# Load basic Python modules
import os, sys, re, time, magic, multiprocessing

# Load Uforia custom modules
import config, File, hash, macs, modscanner
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")

from hash import *
from macs import *
from Uforia.models import * 
from Uforia.modules.models import *

class Uforia(object):
    def __init__(self):
        self.tasks =  multiprocessing.JoinableQueue()
        self.consumers = [Consumer(self.tasks) for i in xrange(config.CONSUMERS)]
        if config.DEBUG:
            print "Starting File Worker..."
        self.fileScanner(config.STARTDIR)
        for w in self.consumers:
            w.start()
        self.tasks.join()

    def fileScanner(self,dir):
        if config.DEBUG:
            print "Starting in directory "+config.STARTDIR+"..."
            print "Starting Filepath Scanner..."
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath=os.path.join(root,name)
                self.tasks.put(self.fileProcessor(fullpath))
                if config.DEBUG:
                    print "Added:",fullpath
        return
    
    def fileProcessor(self,fullpath):
        self.file = File.File(fullpath)
    
        hash = Hash(MD5 = self.file.md5, SHA1 = self.file.sha1, SHA256 = self.file.sha256, FileType = self.file.mtype, FileSize = self.file.size)
        try:
	        hash.save()
	        if config.DEBUG: print "\n","\n","Hashes exported to database"
	        if config.DEBUG: print "Metadata exported to database"
	        metadata = Metadata(Location = self.file.fullpath, Name = self.file.name, MTimes = self.file.mtime, ATimes = self.file.atime, CTimes = self.file.ctime, Owner = self.file.owner, Groups = self.file.group, Permissions = '?')
	        metadata.save()
        except:
	        if config.DEBUG: print "\nError storing hashes or metadata in the database."
    
        xmtype = ''.join(e for e in self.file.mtype if e.isalnum())
        if config.DEBUG: print "\n","Clean Filetype: ", xmtype
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
					
class Consumer(multiprocessing.Process):
    def __init__(self, task_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue

    def run(self):
        print "Getting items: ",self.task_queue.qsize()
        while not self.task_queue.empty():
            next_task = self.task_queue.get()
            self.task_queue.task_done()
            if not next_task:
                break
            next_task()

if __name__ == "__main__":
    modscanner.findmods(modscanner.modtop)
    main = Uforia()
