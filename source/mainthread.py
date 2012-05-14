#!/usr/bin/python

import os, sys, Queue, threading, re, time
from md5 import md5calc
import magic
from hash import filetomd5
from macs import *

fileList = []
rootDir = sys.argv[0]
top = os.getcwd()
nameThread = threading.currentThread().getName()

class Recurser(threading.Thread):
	def __init__(self, queue, dir):
		self.queue = queue
		self.dir = dir
		threading.Thread.__init__(self)
		
	def run(self):
			print nameThread + ": adding to que started"
			self.addToQueue(self.dir)
			print nameThread + ": adding to queue completed"
		            
	def addToQueue(self, topdown=False):
		for root, dirs, files in os.walk(top, topdown=False):
			for name in files:
				self.queue.put(os.path.join(root,name))	
				print nameThread + ": added filepath\t",os.path.join(root,name), "to queue"
		
class Scanner(threading.Thread):
	def __init__(self, queue):
			print nameThread + ": starting new thread to hash files"
			threading.Thread.__init__(self)
			self.queue = queue
		
	def run(self):
		nextFile = self.queue.get()
		while nextFile:
			try:	
				print "\n", nameThread, ": Trying " + nextFile
				self.scanFile(nextFile)
				nextFile = self.queue.get()
			except:
				print nameThread + ": failed to scan file:", sys.exc_info()[0]
				raise
			

	def scanFile(self, name):
			filepath = self.queue.get()
			ftype = magic.from_file(filepath)
			mtype = magic.from_file(filepath, mime=True)
			btype = magic.from_buffer(open(filepath).read(1024))
			print nameThread + ": hashes:", filetomd5(filepath),
			print "\n", nameThread, ": file magic:", ftype, mtype, btype,
			print "\n", nameThread, ": modified:", mtime(filepath),
			print "\n", nameThread, ": metadata change:", ctime(filepath),
			print "\n", nameThread, ": access time:", atime(filepath),
			print "\n", nameThread, ": user id and group id:", owner(filepath), group(filepath),
			print "\n", nameThread, ": current directory is:", top
				
fileQueue = Queue.Queue()

print nameThread + ": starting recurser"
for recurser in xrange(0,1):
	recurser = Recurser(fileQueue, rootDir)
	recurser.start()
	print nameThread + ": recurser started"
else:
	recurser.join()

#recurser = Recurser(fileQueue,rootDir)
#recurser.start()

print nameThread + ": starting scanner"
for scanner in xrange(0,1):
	scanner = Scanner(fileQueue)
	scanner.start()
	print nameThread + ": scanner started"
else:
	scanner.join()
