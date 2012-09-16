#!/usr/bin/env python

"""
All the 'print' lines are used for debug purposes
"""

import os, sys, re, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")

import magic
import multiprocessing
from hash import *
from macs import *
from modscanner import *
from Uforia.models import * 
from Uforia.modules.models import *
from config import *

rootDir = sys.argv[0]
top = os.getcwd()
#The directory to start can be configured in the config.py file
start = startScan
findmods(modtop)

class Uforia:
    def run(self):
        self.number = 0
        self.tasks =  multiprocessing.JoinableQueue()
        self.consumers = [Consumer(self.tasks) for i in xrange(numberOfWorkers)]
        if debug: print "\n","Starting File Worker"
        for w in self.consumers:
            w.start()
        self.fileScanner(start)    
        self.tasks.join()

    def fileScanner(self,dir):
        if debug: print "\n","Starting in directory:", startScan
        if debug: print "\n","Starting Filepath Scanner"
        filelist = []
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                file=os.path.join(root,name)
                filelist.append(file)
                if debug: print "Successfully added filepath\t",os.path.join(root,name), "to queue"
        for file in filelist:
                    self.tasks.put(self.fileProcessor(file))
        return
    
    def fileProcessor(self,filepath):
        self.number = self.number + 1
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
        if debug: print "\n","file name:", name,
        if debug: print "\n","MD5 Hash:", md5,
        if debug: print "\n","SHA1 Hash:", sha1,
        if debug: print "\n","SHA256 Hash:", sha256,
        if debug: print "\n","\n","File magic:", ftype, mtype, btype, #filetype,
        if debug: print "\n","\n","Modified:", mtimes,
        if debug: print "\n","Metadata change:", ctimes,
        if debug: print "\n","Access time:", atimes,
        if debug: print "\n","User id and group id:", fileowner, filegroup,
    
        #This part of code exports the calculated hashes to the database
    
        hash = Hash(MD5 = md5, SHA1 = sha1, SHA256 = sha256, FileType = mtype, FileSize = filesize)
        hash.save()
        if debug: print "\n","\n","Hashes exported to database"
        #This part of code exports the metadata of the file to the database
        metadata = Metadata(Location = filepath, Name = name, MTimes = mtimes, ATimes = atimes, CTimes = ctimes, Owner = fileowner, Groups = filegroup, Permissions = '?')
        metadata.save()
        if debug: print "Metadata exported to database"
    
        #This part of code cleans up the full magic output to an easy to understand string for the 'modscanner', so the right module will be selected to read the file contents
        xmtype = ''.join(e for e in mtype if e.isalnum())
        if debug: print "\n","Clean Filetype: ", xmtype
        externalresult = xmtype
        #This part of code tries to search the right module for the file, to read the contents
        try:
            result = modname.index(externalresult)
            rt = result + 1
            resulttest = modname[rt]
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
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                self.task_queue.task_done()
                break
            next_task()
            self.task_queue.task_done()
        return




if __name__ == "__main__":
    main = Uforia()
    main.run()
    


	


