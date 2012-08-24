#!/usr/bin/env python

import os

#The program is looking for its own root folder and then it goes to the /modules directory
modtop = top=os.getcwd()
modtop +="/modules"
moddir = []
modname = []

#This part of code will scan all the directories for the right Module name and will enter this directory
def findmods(modtop):
	for root, dirs, files in os.walk(modtop, topdown=False):
			
		for name in dirs:
			modtop=os.path.join(root,name)
			modname.append(name)
			try:
				module = os.path.isdir(modtop)
			except ModuleException:
				print "Error parsing stream"
			else:
				if module:
					moddir.append(modtop)
				else: 
					print "fail"
			findexec(modtop)

#This part of code will find the executable file in the previous found directory, to handle the file found by the Uforia main program
def findexec(modtop):
	for root, dirs, files in os.walk(modtop, topdown=False):
		for name in files:
			filepath=os.path.join(root,name)
			mods = []
			mods.append(filepath)
			modname.extend(mods)

#For debug reasons, the output will be shown
"""                                                                        
findmods(modtop)

#print len(modname)
#print "modname:", modname
#print len(moddir)
#print "moddir:",  moddir
result = modname.index(externalresult)
#print "result: ", result 
rt = result + 1
#print "rt: ", rt
#print "modname x = ", modname[rt]
resulttest = modname[rt]
er = "modules/"
er += externalresult
if externalresult in resulttest:
	os.system('resulttest "filepath"')

"""
