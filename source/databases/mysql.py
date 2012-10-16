#!/usr/bin/env python

import warnings, sys
sys.path.append('.')

class Database(object):
    def __init__(self,config):
        if not config.DBHOST or not config.DBUSER or not config.DBPASS or not config.DBNAME:
            raise ValueError('Cannot initialize a database connection without valid credentials.')
        else:
            self.hostname = config.DBHOST
            self.username = config.DBUSER
            self.password = config.DBPASS
            self.database = config.DBNAME
            self.truncate = config.TRUNCATE
            try:
                import MySQLdb
            except ImportError:
                raise
            try:
                self.db=MySQLdb.connect(host=self.hostname,user=self.username,passwd=self.password,db=self.database)
            except:
                raise
    
    def filestable(self):
        self.cursor = self.db.cursor()
        query="""CREATE TABLE IF NOT EXISTS `files`
            (`hashid` BIGINT UNSIGNED NOT NULL PRIMARY KEY,
            INDEX USING HASH (`hashid`),
            `fullpath` LONGTEXT,
            `name` LONGTEXT,
            `size` BIGINT,
            `owner` INT,
            `group` INT,
            `perm` LONGTEXT,
            `mtime` DECIMAL(32,16),
            `atime` DECIMAL(32,16),
            `ctime` DECIMAL(32,16),
            `md5` VARCHAR(32),
            `sha1` VARCHAR(40),
            `sha256` VARCHAR(64),
            `ftype` LONGTEXT,
            `mtype` LONGTEXT,
            `btype` LONGTEXT)"""
        warnings.filterwarnings('ignore',category=self.db.Warning)
        self.cursor.execute(query)
        self.db.commit()
        if self.truncate:
            query="""TRUNCATE `files`"""
            warnings.filterwarnings('ignore',category=self.db.Warning)
            self.cursor.execute(query)
            self.db.commit()
        warnings.resetwarnings()

    def setup(self,moduletable,columns):
        if not self.db:
            raise
        if not moduletable:
            raise ValueError('Module table name missing.')
        if not columns:
            raise ValueError('Table columns missing.')
        query="""CREATE TABLE IF NOT EXISTS `"""+moduletable+"""` (`hashid` BIGINT UNSIGNED NOT NULL, INDEX USING HASH (`hashid`)"""
        for items in columns.split(','):
            name,type=items.split(':')
            query=query+""", `"""+name+"""` """+type
        query=query+""", PRIMARY KEY(`hashid`));"""
        warnings.filterwarnings('ignore',category=self.db.Warning)
        self.cursor.execute(query)
        self.db.commit()
        if self.truncate:
            query="""TRUNCATE `"""+moduletable+"""`"""
            warnings.filterwarnings('ignore',category=self.db.Warning)
            self.cursor.execute(query)
            self.db.commit()
        warnings.resetwarnings()

    def store(self,moduletable,hashid,columns,values):
        if not self.db:
            raise
        if not moduletable or not columns or not values:
            raise ValueError('Cannot store information to database.')
        cursor = self.db.cursor()
        query="""INSERT IGNORE INTO `"""+moduletable+"""` ("""
        if hashid:
            query=query+"""`hashid`"""
        for item in columns:
            query=query+", `"+item+"`"
        query=query+""") VALUES ("""
        if hashid:
            query=query+str(hashid)
        for item in values:
            query=query+", '%s'"
        query=query+""");"""
        escaped=[]
        for i in values:
            escaped.append(self.db.escape_string(str(i)))
        escaped=tuple(escaped)
        warnings.filterwarnings('ignore',category=self.db.Warning)
        if not hashid:
            query=query.replace(""" (, """,""" (""")
        cursor.execute(query%escaped)
        warnings.resetwarnings()

    def findhash(self,fullpath):
        if not self.db:
            raise
        cursor = self.db.cursor()
        query="""SELECT hashid FROM files WHERE fullpath='%s';"""
        escaped=[]
        for item in fullpath:
            escaped.append(self.db.escape_string(item))
        escaped=tuple(escaped)
        cursor.execute(query%escaped)
        return self.cursor.fetchone()[0]
