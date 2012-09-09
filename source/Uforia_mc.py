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


def makelist(dir):
    filelist = []
    for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
        for name in files:
            file=os.path.join(root,name)
            filelist.append(file)
            if debug: print "Successfully added filepath\t",os.path.join(root,name), "to queue"
    
    return filelist

					
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

class fileProcessor(object):
    
    def __init__(self,filepath):
        self.filepath = filepath
    
    def __call__(self):
        ftype = magic.from_file(self.filepath)
        mtype = magic.from_file(self.filepath, mime=True)
        btype = magic.from_buffer(open(self.filepath).read(1024))
        md5 = filetomd5(self.filepath)
        sha1 = filetosha1(self.filepath)
        sha256 = filetosha256(self.filepath)
        mtimes = mtime(self.filepath)
        ctimes = ctime(self.filepath)
        atimes = atime(self.filepath)
        fileowner = owner(self.filepath)
        filegroup = group(self.filepath)
        filesize = os.path.getsize(self.filepath)
        name = os.path.basename(self.filepath)
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
        metadata = Metadata(Location = self.filepath, Name = name, MTimes = mtimes, ATimes = atimes, CTimes = ctimes, Owner = fileowner, Groups = filegroup, Permissions = '?')
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

#To prevent an endless loop when processing .zip, .tar or .rar files, the threads can only be started when Uforia is executed as main
#When processing .zip, .tar or .rar files, one single thread should be started by the main program to process the contents of the file. 
if __name__ == "__main__":
    
    tasks =  multiprocessing.JoinableQueue()
    consumers = [Consumer(tasks) for i in xrange(numberOfWorkers)]

    for w in consumers:
        w.start()
        
    if debug: print "\n","Starting in directory:", startScan
    if debug: print "\n","Starting Filepath Scanner"

    workList = makelist(start)

    if debug: print "\n","Starting File Worker"

    for file in workList:
        tasks.put(fileProcessor(file))

    for i in xrange(numberOfWorkers):
        tasks.put(None)

    tasks.join()
	


