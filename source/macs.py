#!/usr/bin/env python

import os
import datetime
import pwd
from stat import *

#This part of code will get the 'modification time' of a file
def mtime(filepath):
	mt = os.path.getmtime(filepath)
	mres  = datetime.datetime.fromtimestamp(mt)
	return mres

#This part of code will get the 'change time' or 'creation time' of a file
#On UNIX systems it will show the last change of the file metadata and not the file contents
#On Windows systems it will show the 'creation time', also called 'birth time'
def ctime(filepath):
	ct = os.path.getctime(filepath)
	return datetime.datetime.fromtimestamp(ct)

#This will show the 'access time' of a file
#This means when the file was most recently opened for reading
def atime(filepath):
	at = os.path.getatime(filepath)
	return datetime.datetime.fromtimestamp(at)

#This will show the 'owner' of a file
def owner(filepath):
	oinfo = os.stat(filepath)
	uid = oinfo.st_uid
	return uid

#This will show the 'group' the file belongs to
def group(filepath):
	ginfo = os.stat(filepath)
	gid = ginfo.st_gid
	return gid
	
#For debug reasons, the output will be shown
"""
mres = mtime(filepath)
cres = ctime(filepath)
ares = atime(filepath)
own = owner(filepath)
grp = group(filepath)

print "modification times: ", mres
print "creation/inode change times: ", cres
print "acces time: ", ares
print "owner id: ", own
print "group id: ", grp
"""
