#!/usr/bin/python

import os, sys, Queue, threading, re, time
#sys.path.append('/home/chris/') #koppeling naar django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings") #settingsdatabase

import magic
from hash import *
from macs import *
from Uforia.models import * #import Hash model
#from md5 import md5calc

fileList = []
rootDir = sys.argv[0]
top = os.getcwd()
start = '/'
nameThread = threading.currentThread().getName()

class Scanner(threading.Thread):
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
				
class Hasher(threading.Thread):
	def __init__(self, queue):
			threading.Thread.__init__(self)
			self.queue = queue
		
	def run(self):
		nextFile = self.queue.get()
		while nextFile:
			try:	
				print "\n","\n","Trying " + nextFile
				self.scanFile(nextFile)
				nextFile = self.queue.get()
				self.queue.task_done()
				print "\n","Hashing of this file successfull"
			except:
				print "Failed to scan file:", "/n",sys.exc_info()[0]
				nextFile = self.queue.get()
				self.queue.task_done()
				pass
			
	def scanFile(self, name):
			filepath = self.queue.get()
			ftype = magic.from_file(filepath)
			mtype = magic.from_file(filepath, mime=True)
			btype = magic.from_buffer(open(filepath).read(1024))
			
			print "\n", "MD5 Hash:", filetomd5(filepath),
			print "\n", "SHA1 Hash:", filetosha1(filepath),
			print "\n", "SHA256 Hash:", filetosha256(filepath),
			print "\n","File magic:", ftype, mtype, btype, #filetype,
			print "\n","Modified:", mtime(filepath),
			print "\n","Metadata change:", ctime(filepath),
			print "\n","Access time:", atime(filepath),
			print "\n","User id and group id:", owner(filepath), group(filepath),

			b = Hash(MD5 = filetomd5(filepath), SHA1 = filetosha1(filepath), SHA256 = filetosha256(filepath), FileType = '1', FileSize = '123456')
			b.save()
			print "\n","Hashes exported to database"
			c = Metadata(Location = filepath, Name = os.path.basename(filepath), MTimes = mtime(filepath), ATimes = atime(filepath), CTimes = ctime(filepath), Owner = owner(filepath), Groups = group(filepath), Permissions = '?')
			c.save()
			print "\n","Metadata exported to database"

fileQueue = Queue.Queue()

print "\n","Starting in directory:", start
print "\n","Starting Scanner"
for scanner in xrange(1):
	scanner = Scanner(fileQueue, rootDir)
	scanner.start()
	print "\n","Scanner started successfully"
	scanner.join()
	print "\n","Stopping Scanner"
	
print "\n","Starting Hasher"
for hasher in xrange(1):
	hasher = Hasher(fileQueue)
	hasher.start()
	print "\n","Hasher started successfully"
	hasher.join()
	print "\n","Stopping Hasher"
