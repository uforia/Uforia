#!/usr/bin/env python

#TABLE: Contents:LONGTEXT

def process(fullpath,hashid,db,tablename):
    with open(fullpath,'rb') as f:
        return f.read()
