#!/usr/bin/env python

import hashlib

#This part of code will calculate the MD5 of a file
def filetomd5(filepath):
	md5 = hashlib.md5()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			md5.update(chunk)
	return md5.hexdigest() 

#This part of code will calculate the SHA1 of a file
def filetosha1(filepath):
	sha1 = hashlib.sha1()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			sha1.update(chunk)
	return sha1.hexdigest() 
	
#This part of code will calculate the SHA256 of a file
def filetosha256(filepath):
	sha256= hashlib.sha256()
	with open(filepath,'rb') as f: 
		for chunk in iter(lambda: f.read(8192), b''): 
			sha256.update(chunk)
	return sha256.hexdigest() 
