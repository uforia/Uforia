#!/usr/bin/env python

# DB: SEARCHABLETEXT

def process(fullpath):
    with open(fullpath,'rb') as f:
        fulltext=f.read()
        print fulltext
