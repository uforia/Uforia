#!/usr/bin/env python

try:
    import MySQLdb, warnings, time
except:
    raise

class Database(object):
    def __init__(self,config):
        if not config.DBHOST or not config.DBUSER or not config.DBPASS or not config.DBNAME:
            raise ValueError('Cannot initialize a database connection without valid credentials.')
        else:
            self.hostname   = config.DBHOST
            self.username   = config.DBUSER
            self.password   = config.DBPASS
            self.database   = config.DBNAME
            self.truncate   = config.TRUNCATE
            self.debug      = config.DEBUG
    
    def executeQuery(self,query):
        connection = None
        while not connection:
            try:
                connection = MySQLdb.connect(host=self.hostname,user=self.username,passwd=self.password,db=self.database)
            except MySQLdb.OperationalError, e:
                if self.debug or True:
                    print("Could not connect to the MySQL server: "+str(e))
                    print("You might be flooding it with connections; consider raising the maximum amount!")
                    print("Sleeping briefly...")
                    time.sleep(1)
            except:
                raise
        try:
            connection = MySQLdb.connect(host=self.hostname,user=self.username,passwd=self.password,db=self.database)
        except:
            raise
        try:
            cursor = connection.cursor()
        except:
            raise
        try:
            warnings.filterwarnings('ignore',category=connection.Warning)
            cursor.execute(query)
            connection.commit()
            warnings.resetwarnings()
            connection.close()
        except:
            raise
    
    def setupMainTable(self):
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
        self.executeQuery(query)
        if self.truncate:
            query = """TRUNCATE `files`"""
            self.executeQuery(query)

    def setupModuleTable(self,table,columns):
        if not table or not columns:
            raise ValueError('Module table or columns missing.')
        query = """CREATE TABLE IF NOT EXISTS `"""+table+"""` (`hashid` BIGINT UNSIGNED NOT NULL, INDEX USING HASH (`hashid`)"""
        for items in columns.split(','):
            name,type = items.split(':')
            query += """, `"""+name+"""` """+type
        query += """, PRIMARY KEY(`hashid`));"""
        self.executeQuery(query)
        if self.truncate:
            query = """TRUNCATE `"""+table+"""`"""
            self.executeQuery(query)

    def store(self,table,hashid,columns,values):
        if not table or not columns or not values:
            raise ValueError('Module table, columns or values missing.')
        query = """INSERT IGNORE INTO `"""+table+"""` (`hashid`"""
        for item in columns:
            query += ", `"+item+"`"
        query += """) VALUES ("""+str(hashid)
        for item in values:
            query += ", '%s'"
        query += """);"""
        escaped = []
        for i in values:
            escaped.append(MySQLdb.escape_string(str(i)))
        escaped = tuple(escaped)
        escapedQuery = query%escaped
        escapedQuery = escapedQuery.replace(""" (, """,""" (""")
        self.executeQuery(escapedQuery)
