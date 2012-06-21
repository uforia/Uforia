#!/usr/bin/env python

import hashlib
#Get file md5
def filetomd5(filepath):
	md5 = hashlib.md5()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			md5.update(chunk)
	return md5.hexdigest() 
#Get file sha1
def filetosha1(filepath):
	sha1 = hashlib.sha1()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			sha1.update(chunk)
	return sha1.hexdigest() 
	
#get file sha256
def filetosha256(filepath):
	sha256= hashlib.sha256()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			sha256.update(chunk)
	return sha256.hexdigest() 
