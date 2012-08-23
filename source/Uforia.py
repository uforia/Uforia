#!/usr/bin/python

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
start = startScan
nameThread = threading.currentThread().getName()
findmods(modtop)

class filepathScanner(threading.Thread):
	def __init__(self, queue, dir):
		threading.Thread.__init__(self)
		self.queue = queue
		self.dir = dir
		
	def run(self):
			print "Adding filepaths to queue"
			self.addToQueue(self.dir)
			print "Adding filepaths to queue done"
					            
	def addToQueue(self, topdown=True):
		for root, dirs, files in os.walk(start, topdown=True, followlinks=False):
			for name in files:
				self.queue.put(os.path.join(root,name))	
				print "Successfully added filepath\t",os.path.join(root,name), "to queue"
				
class fileWorker(threading.Thread):
	def __init__(self, queue):
			threading.Thread.__init__(self)
			self.queue = queue
		
	def run(self):
		while self.queue.qsize():
			try:	
				nextFile = self.queue.get()
				print "\n","\n","\n","---------------------------------------------"
				print "Trying " + nextFile
				self.workFile(nextFile)
				self.queue.task_done()
				print "\n", "File Worker successfully processed this file"
				print "Queue items left: ", self.queue.qsize()
				print "---------------------------------------------"
			except:
				print "\n","File Worker failed to proces file:", "\n",sys.exc_info()[0]
				self.queue.task_done()
				print "Queue items left: ", self.queue.qsize()
				pass
					
			
	def workFile(self, nextFile):
			filepath = nextFile
			ftype = magic.from_file(filepath)
			mtype = magic.from_file(filepath, mime=True)
			btype = magic.from_buffer(open(filepath).read(1024))
			
			print "\n","MD5 Hash:", filetomd5(filepath),
			print "\n","SHA1 Hash:", filetosha1(filepath),
			print "\n","SHA256 Hash:", filetosha256(filepath),
			print "\n","\n","File magic:", ftype, mtype, btype, #filetype,
			print "\n","\n","Modified:", mtime(filepath),
			print "\n","Metadata change:", ctime(filepath),
			print "\n","Access time:", atime(filepath),
			print "\n","User id and group id:", owner(filepath), group(filepath),

			b = Hash(MD5 = filetomd5(filepath), SHA1 = filetosha1(filepath), SHA256 = filetosha256(filepath), FileType = mtype, FileSize = os.path.getsize(filepath))
			b.save()
			print "\n","\n","Hashes exported to database"
			c = Metadata(Location = filepath, Name = os.path.basename(filepath), MTimes = mtime(filepath), ATimes = atime(filepath), CTimes = ctime(filepath), Owner = owner(filepath), Groups = group(filepath), Permissions = '?')
			c.save()
			print "Metadata exported to database"
			
			xmtype = ''.join(e for e in mtype if e.isalnum())
			print "\n","Clean Filetype: ", xmtype
			externalresult = xmtype
			
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
		
fileQueue = Queue.Queue()

if __name__ == "__main__": 

	print "\n","Starting in directory:", startScan
	print "\n","Starting Filepath Scanner"
	for scanner in xrange(numberOfScanners):
			scanner = filepathScanner(fileQueue, rootDir)
			scanner.start()
	print "\n","Filepath Scanner started successfully"
	scanner.join()
	print "\n","Stopping Filepath Scanner"
	
	print "\n","Starting File Worker"
	for hasher in xrange(numberOfWorkers):
		hasher = fileWorker(fileQueue)
		hasher.start()
	print "\n","File Worker started successfully"
	hasher.join()
	print "\n","Stopping File Worker"
