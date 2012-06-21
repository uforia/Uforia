import os

modtop = top=os.getcwd()
modtop +="/modules"
moddir = []
modname = []

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

def findexec(modtop):
	for root, dirs, files in os.walk(modtop, topdown=False):
		for name in files:
			filepath=os.path.join(root,name)
			mods = []
			mods.append(filepath)
			modname.extend(mods)
#			print "totaal:", moddir
#			print "bestanden:", mods
			#print "mod found: ", os.path.join(root,name)
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
