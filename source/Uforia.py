#!/usr/bin/env python

"""
All the 'print' lines are used for debug purposes
"""

import os, sys, Queue, threading, re, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")

import magic
from hash import *
from macs import *
from modscanner import *
from Uforia.default.models import * 
from Uforia.modules.models import *
from config import *

fileList = []
rootDir = sys.argv[0]
top = os.getcwd()
#The directory to start can be configured in the config.py file
start = startScan
findmods(modtop)


#This class is responsible for the inventarisation of all the files in the filesystem
class filepathScanner(threading.Thread):
	def __init__(self, queue, dir):
		threading.Thread.__init__(self)
		self.queue = queue
		self.dir = dir

#This part of code starts adding the filepaths found to the queue		
	def run(self):
            if debug: print "Adding filepaths to queue"
            self.addToQueue(self.dir)
            if debug: print "Adding filepaths to queue done"

#This part of code walks through the filesystem looking for files and will add the filepath to the queue					            
	def addToQueue(self, topdown=True):
		for root, dirs, files in os.walk(start, topdown=True, followlinks=False):
			for name in files:
				self.queue.put(os.path.join(root,name))	
				if debug: print "Successfully added filepath\t",os.path.join(root,name), "to queue"

#This class is responsible for the processing of all the files in the queue				
class fileWorker(threading.Thread):
	def __init__(self, queue):
			threading.Thread.__init__(self)
			self.queue = queue

#This part of code starts processing all the files in the queue 		
	def run(self):
		#As long there is something in the queue start the following code:
		while self.queue.qsize():
			try:	
				#nextFile is the first filepath in row obtained from the queue
				nextFile = self.queue.get()
				if debug: print "\n","\n","\n","---------------------------------------------"
				if debug: print "Trying " + nextFile
				self.workFile(nextFile)
				self.queue.task_done()
				if debug: print "\n", "File Worker successfully processed this file"
				#This shows how much queue items are left
				if debug: print "Queue items left: ", self.queue.qsize()
				if debug: print "---------------------------------------------"
			#When the processing of a file failes, the program will show the reason why and skips the current filepath, so the program will continue with the first filepath in row
			except:
				if debug: print "\n","File Worker failed to proces file:", "\n",sys.exc_info()[0]
				self.queue.task_done()
				if debug: print "Queue items left: ", self.queue.qsize()
				pass
					
			
	def workFile(self, nextFile):
            filepath = nextFile
            ftype = magic.from_file(filepath)
            mtype = magic.from_file(filepath, mime=True)
            btype = magic.from_buffer(open(filepath).read(1024))
            md5 = filetomd5(filepath)
            sha1 = filetosha1(filepath)
            sha256 = filetosha256(filepath)
            mtime = mtime(filepath)
            ctime = ctime(filepath)
            atime = atime(filepath)
            owner = owner(filepath)
            group = group(filepath)
            filesize = os.path.getsize(filepath)
            name = os.path.basename(filepath)
            if debug: print "\n","MD5 Hash:", md5,
            if debug: print "\n","SHA1 Hash:", sha1,
            if debug: print "\n","SHA256 Hash:", sha256,
            if debug: print "\n","\n","File magic:", ftype, mtype, btype, #filetype,
            if debug: print "\n","\n","Modified:", mtime,
            if debug: print "\n","Metadata change:", ctime,
            if debug: print "\n","Access time:", atime,
            if debug: print "\n","User id and group id:", owner, group,

			#This part of code exports the calculated hashes to the database
            hash = Hash(MD5 = md5, SHA1 = sha1, SHA256 = sha256, FileType = mtype, FileSize = filesize)
            hash.save()
            if debug: print "\n","\n","Hashes exported to database"
            #This part of code exports the metadata of the file to the database
            metadata = Metadata(Location = filepath, Name = name, MTimes = mtime, ATimes = atime, CTimes = ctime, Owner = owner, Groups = group, Permissions = '?')
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

#To prevent an endless loop when processing .zip, .tar or .rar files, the threads can only be started when Uforia is executed as main
#When processing .zip, .tar or .rar files, one single thread should be started by the main program to process the contents of the file. 
if __name__ == "__main__":
				
	fileQueue = Queue.Queue()

if debug: print "\n","Starting in directory:", startScan
if debug: print "\n","Starting Filepath Scanner"
#This part of code will start the threads and will check the config.py file to see how many threads should be started at the same time.
#When the task is done, the threads will end when all the threads are done by the *.join() command
for scanner in xrange(numberOfScanners):
	scanner = filepathScanner(fileQueue, rootDir)
	scanner.start()
	if debug: print "\n","Filepath Scanner started successfully"
	scanner.join()
	if debug: print "\n","Stopping Filepath Scanner"
	
if debug: print "\n","Starting File Worker"
for hasher in xrange(numberOfWorkers):
	hasher = fileWorker(fileQueue)
	hasher.start()
	if debug: print "\n","File Worker started successfully"
	hasher.join()
	if debug: print "\n","Stopping File Worker"
