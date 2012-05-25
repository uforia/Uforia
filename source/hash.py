#!/usr/bin/env python

import hashlib

def filetomd5(filepath):
	md5 = hashlib.md5()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			md5.update(chunk)
	return md5.hexdigest() 

def filetosha1(filepath):
	sha1 = hashlib.sha1()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			sha1.update(chunk)
	return sha1.hexdigest() 
	

def filetosha256(filepath):
	sha256= hashlib.sha256()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			sha256.update(chunk)
	return sha256.hexdigest() 
	
if __name__ == "__main__":
	#filepath = '/home/carlo/test/hashbatch/aap.txt'
	print filetomd5(filepath)
