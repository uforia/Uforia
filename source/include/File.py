#!/usr/bin/env python
# coding: utf-8

# Base Python modules
import os, sys, hashlib, datetime

# Uforia modules
import config, magic

class File(object):
    def __init__(self,filepath=None,DEBUG=False):
        """
        Attempt to parse the file passed via the filepath variable and store its
        name, size, owner, group, MACtimes, MD5/SHA1/SHA256 hashes and file magic
        properties in the object's properties.
        """
        if not filepath:
            pass
        else:
            try:
                self.fullpath = str(filepath)
                self.name = str(os.path.basename(filepath))
                self.size = str(os.path.getsize(filepath))
            except:
                raise IOError('Cannot read basic file information. Permissions problem?')
            try:
                self.owner = str(os.stat(filepath).st_uid)
                self.group = str(os.stat(filepath).st_gid)
            except:
                self.owner = None
                self.group = None
                print('Cannot read owner/group id. File system might not support ownerships.')
            try:
                self.perm = oct(os.stat(filepath).st_mode)
            except:
                self.perm = None
                print('Cannot read permissions. File system might not support permissions.')
            try:
                self.mtime = repr(os.path.getmtime(filepath))
            except:
                self.mtime = None
                print('File system might not support MACtimes.')
            try:
                self.atime = repr(os.path.getatime(filepath))
            except:
                self.atime = None
                print('File system might not support MACtimes.')
            try:
                self.ctime = repr(os.path.getctime(filepath))
            except:
                self.ctime = None
                print('File system might not support MACtimes.')
            try:
                self.md5 = hashlib.md5()
                self.sha1 = hashlib.sha1()
                self.sha256 = hashlib.sha256()
                self.ftype = str(magic.from_file(filepath))
                self.mtype = str(magic.from_file(filepath, mime=True))
                self.btype = str(magic.from_buffer(open(filepath).read(65536)))
                with open(filepath,'rb') as f:
                    for chunk in iter(lambda: f.read(65536), b''):
                        self.md5.update(chunk)
                        self.sha1.update(chunk)
                        self.sha256.update(chunk)
                self.md5 = str(self.md5.hexdigest())
                self.sha1 = str(self.sha1.hexdigest())
                self.sha256 = str(self.sha256.hexdigest())
            except:
                raise IOError('Error calculating digests, possible filesystem error.')
            if DEBUG:
                print "\nFilename:\t",self.name
                print "UID/GID:\t",self.owner+":"+self.group
                print "Permissions:\t",self.perm
                print "Magic:\t\tF:",self.ftype,"\n\t\tM:",self.mtype,"\n\t\tB:",self.btype
                print "Modified:\t",self.mtime,"\nAccessed:\t",self.atime,"\nChanged:\t",self.ctime
                print "MD5:\t\t",self.md5,"\nSHA1:\t\t",self.sha1,"\nSHA256\t\t",self.sha256

if __name__ == "__main__":
    print "This is an example where",sys.argv[0],"creates a File object and examines itself :-)\n"
    DEBUG = True
    example = File(sys.argv[0],DEBUG)
