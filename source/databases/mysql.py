#!/usr/bin/env python

import warnings

class Database(object):
    def __init__(self,host='localhost',user=None,passwd=None,db='Uforia'):
        if not host or not user or not passwd or not db:
            raise ValueError('Cannot initialize a database connection without valid credentials.')
        else:
            self.hostname = host
            self.username = user
            self.password = passwd
            self.database = db
            import MySQLdb
            try:
                self.db=MySQLdb.connect(host=self.hostname,user=self.username,passwd=self.password,db=self.database)
            except:
                raise
            self.cursor = self.db.cursor()

    def setup(self,moduletable,columns):
        if not self.db:
            raise
        if not moduletable:
            raise ValueError('Module table name missing.')
        if not columns:
            raise ValueError('Table columns missing.')
        query="""CREATE TABLE IF NOT EXISTS """+moduletable+""" (hashid BIGINT PRIMARY KEY NOT NULL, INDEX USING HASH (hashid)"""
        for items in columns:
            name,type=items
            query=query+""", """+name+""" """+type
        query=query+""");"""
        warnings.filterwarnings('ignore',category=self.db.Warning)
        self.sql(query)
        warnings.resetwarnings()

    def store(self,moduletable,hashid,values):
        if not self.db:
            raise
        if not moduletable:
            raise ValueError('Module table name missing.')
        if not hashid or not values:
            raise ValueError('Insert values missing.')
        query="""INSERT IGNORE INTO """+moduletable+""" VALUES ("""+hashid
        for item in values:
            query=query+""", '"""+item+"""'"""
        query=query+""");"""
        warnings.filterwarnings('ignore',category=self.db.Warning)
        self.sql(query)
        warnings.resetwarnings()

    def sql(self,query=None):
        if not self.db or not query:
            raise
        try:
            self.cursor.execute(query)
            self.db.commit()
        except:
            raise
