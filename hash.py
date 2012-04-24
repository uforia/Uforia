#!/usr/bin/env python

import hashlib

def filetomd5(filepath):
	md5 = hashlib.md5()
	sha1= hashlib.sha1()
	sha256 = hashlib.sha256()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			md5.update(chunk)
			sha1.update(chunk)
			sha256.update(chunk)
	return md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest()

if __name__ == "__main__":
	#filepath = '/home/carlo/test/hashbatch/aap.txt'
	print filetomd5(filepath)
