#!/usr/bin/env python

# Base Python modules
import os, sys, hashlib, datetime

# Uforia modules
import config, magic

class File(object):
    def __init__(self,filepath=None):
        """
        Attempt to parse the file passed via the filepath variable and store its
        name, size, owner, group, MACtimes, MD5/SHA1/SHA256 hashes and file magic
        properties in the object's properties.
        """
        if not filepath:
            pass
        else:
            try:
                self.name = os.path.basename(filepath)
                self.size = os.path.getsize(filepath)
                self.owner = str(os.stat(filepath).st_uid)
                self.group = str(os.stat(filepath).st_gid)
                self.mtime = repr(os.path.getmtime(filepath))
                self.atime = repr(os.path.getatime(filepath))
                self.ctime = repr(os.path.getctime(filepath))
                self.md5 = hashlib.md5()
                self.sha1 = hashlib.sha1()
                self.sha256 = hashlib.sha256()
                self.ftype = magic.from_file(filepath)
                self.mtype = magic.from_file(filepath, mime=True)
                self.btype = magic.from_buffer(open(filepath).read(65536))
                with open(filepath,'rb') as f:
                    for chunk in iter(lambda: f.read(65536), b''):
                        self.md5.update(chunk)
                        self.sha1.update(chunk)
                        self.sha256.update(chunk)
                self.md5 = self.md5.hexdigest()
                self.sha1 = self.sha1.hexdigest()
                self.sha256 = self.sha256.hexdigest()
                if config.DEBUG:
                    print "Filename:\t", self.name
                    print "MD5:\t\t", self.md5
                    print "SHA1:\t\t", self.sha1
                    print "SHA256:\t\t", self.sha256
                    print "Magic:\t\t", self.ftype, self.mtype, self.btype
                    print "Modified:\t", self.mtime
                    print "Accessed:\t", self.atime
                    print "Changed:\t", self.ctime
                    print "UID/GID:\t", self.owner+":"+self.group
            except IOError as detail:
                print "Error opening "+filepath+":", detail

if __name__ == "__main__":
    print "This is an example where file.py creates a File object and examines itself :-)\n"
    example = File(sys.argv[0])
