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
        for items in columns.split(','):
            name,type=items.split(':')
            query=query+""", """+name+""" """+type
        query=query+""");"""
        warnings.filterwarnings('ignore',category=self.db.Warning)
        self.cursor.execute(query)
        self.db.commit()
        warnings.resetwarnings()

    def store(self,moduletable,hashid,columns,values):
        if not self.db:
            raise
        if not moduletable or not hashid or not columns or not values:
            raise ValueError('Cannot store information to database.')
        query="""INSERT IGNORE INTO """+moduletable+""" (hashid"""
        for item in columns:
            query=query+", "+item
        query=query+""") VALUES ("""+str(hashid)
        for item in values:
            query=query+", '%s'"
        query=query+""");"""
        escaped=[]
        for i in values:
            escaped.append(self.db.escape_string(i))
        escaped=tuple(escaped)
        warnings.filterwarnings('ignore',category=self.db.Warning)
        self.cursor.execute(query%escaped)
        self.db.commit()
        warnings.resetwarnings()
