import os
import datetime
import pwd
from stat import *

#contains various file information

def mtime(filepath):
	mt = os.path.getmtime(filepath)
	mres  = datetime.datetime.fromtimestamp(mt)
	return mres

def ctime(filepath):
	ct = os.path.getctime(filepath)
	return datetime.datetime.fromtimestamp(ct)

def atime(filepath):
	at = os.path.getatime(filepath)
	return datetime.datetime.fromtimestamp(at)

def owner(filepath):
	oinfo = os.stat(filepath)
	uid = oinfo.st_uid
	return uid

def group(filepath):
	ginfo = os.stat(filepath)
	gid = ginfo.st_gid
	return gid
	
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
