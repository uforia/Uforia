#!/usr/bin/env python

#TABLE: Contents:LONGTEXT

def process(fullpath):
    with open(fullpath,'rb') as f:
        values=f.read()
        return (values,)
