#!/usr/bin/env python

"""
All 'print' lines are used for debug purposes
"""

import os, sys, re, time, magic, multiprocessing
import config, file, hash, macs, modscanner
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")

from hash import *
from macs import *
from Uforia.models import * 
from Uforia.modules.models import *

class Uforia:
    def __init__(self):
        self.tasks =  multiprocessing.JoinableQueue()
        self.consumers = [Consumer(self.tasks) for i in xrange(config.CONSUMERS)]
        if config.DEBUG: print "\n","Starting File Worker"
        self.fileScanner(config.STARTDIR)
        for w in self.consumers:
            w.start()
        self.tasks.join()

    def fileScanner(self,dir):
        if config.DEBUG: print "\n","Starting in directory:", config.STARTDIR
        if config.DEBUG: print "\n","Starting Filepath Scanner"
        filelist = []
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                file=os.path.join(root,name)
                filelist.append(file)
                if config.DEBUG: print "Added:\t",os.path.join(root,name)
        for file in filelist:
            self.tasks.put(self.fileProcessor(file))
        return
    
    def fileProcessor(self,filepath):
        ftype = magic.from_file(filepath)
        mtype = magic.from_file(filepath, mime=True)
        btype = magic.from_buffer(open(filepath).read(1024))
        md5 = filetomd5(filepath)
        sha1 = filetosha1(filepath)
        sha256 = filetosha256(filepath)
        mtimes = mtime(filepath)
        ctimes = ctime(filepath)
        atimes = atime(filepath)
        fileowner = owner(filepath)
        filegroup = group(filepath)
        filesize = os.path.getsize(filepath)
        name = os.path.basename(filepath)
        if config.DEBUG: print "\n","file name:", name,
        if config.DEBUG: print "\n","MD5 Hash:", md5,
        if config.DEBUG: print "\n","SHA1 Hash:", sha1,
        if config.DEBUG: print "\n","SHA256 Hash:", sha256,
        if config.DEBUG: print "\n","\n","File magic:", ftype, mtype, btype, #filetype,
        if config.DEBUG: print "\n","\n","Modified:", mtimes,
        if config.DEBUG: print "\n","Metadata change:", ctimes,
        if config.DEBUG: print "\n","Access time:", atimes,
        if config.DEBUG: print "\n","User id and group id:", fileowner, filegroup,
    
        hash = Hash(MD5 = md5, SHA1 = sha1, SHA256 = sha256, FileType = mtype, FileSize = filesize)
        try:
	        hash.save()
	        if config.DEBUG: print "\n","\n","Hashes exported to database"
	        if config.DEBUG: print "Metadata exported to database"
	        metadata = Metadata(Location = filepath, Name = name, MTimes = mtimes, ATimes = atimes, CTimes = ctimes, Owner = fileowner, Groups = filegroup, Permissions = '?')
	        metadata.save()
        except:
	        if config.DEBUG: print "\nError storing hashes or metadata in the database."
    
        xmtype = ''.join(e for e in mtype if e.isalnum())
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
            if not next_task: break
            next_task()

if __name__ == "__main__":
    modscanner.findmods(modscanner.modtop)
    main = Uforia()
