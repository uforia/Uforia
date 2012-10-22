#!/usr/bin/env python

#TABLE: Contents:LONGTEXT

def process(table,hashid,columns,fullpath):
    with open(fullpath,'rb') as f:
        values=f.read()
        return (table,hashid,(columns,),(values,))
