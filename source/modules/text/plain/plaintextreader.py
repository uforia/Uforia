#!/usr/bin/env python

#TABLE: Contents:LONGTEXT

def process(db,table,hashid,columns,fullpath):
    with open(fullpath,'rb') as f:
        values=(f.read(),)
        db.store(table,hashid,(columns,),(values,))
