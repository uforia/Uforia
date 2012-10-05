#!/usr/bin/env python

# TEXT

def process(fullpath,hashid,db,modulename):
    with open(fullpath,'rb') as f:
        fulltext=f.read()
        print hashid,db,modulename
