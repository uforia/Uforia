#!/usr/bin/env python

# This is an example module

#TABLE: Contents:LONGTEXT

def process(fullpath):
    with open(fullpath,'rb') as f:
        values=f.read()
        return (values,)
