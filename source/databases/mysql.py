#!/usr/bin/env python

try:
    import MySQLdb, warnings, time
except:
    raise

class Database(object):
    """
    This is a MySQL implementation of Uforia's data storage facility.
    """
    def __init__(self,config):
        """
        Initializes a MySQL database connection using the specified Uforia
        configuration.

        config - The uforia configuration object
        """
        if not config.DBHOST or not config.DBUSER or not config.DBPASS or not config.DBNAME:
            raise ValueError('Cannot initialize a database connection without valid credentials.')
        else:
            hostname        = config.DBHOST
            username        = config.DBUSER
            password        = config.DBPASS
            database        = config.DBNAME
            self.truncate   = config.TRUNCATE
            self.droptable  = config.DROPTABLE
            self.debug      = config.DEBUG
            self.connection = None
            attempts        = 0
            retries         = config.DBRETRY
        while not self.connection:
            try:
                self.connection  = MySQLdb.connect(host = hostname, user = username, passwd = password, db = database)
                attempts    += 1
            except MySQLdb.OperationalError, e:
                if self.debug:
                    print("Could not connect to the MySQL server: "+str(e))
                    print("Sleeping for 3 seconds...")
                time.sleep(3)
                if attempts > retries:
                    print("The MySQL server didn't respond after "+str(retries)+" requests; you might be flooding it with connections.")
                    print("Consider raising the maximum amount of connections on your MySQL server or lower the amount of concurrent Uforia threads!")
                    raise
        try:
            self.cursor     = self.connection.cursor()
        except:
            raise

    def executeQuery(self,query):
        """
        Executes a query (which should have no data to return).

        query - The query string
        """
        try:
            warnings.filterwarnings('ignore',category=self.connection.Warning)
            self.cursor.execute(query)
            warnings.resetwarnings()
        except:
            raise

    def setupMainTable(self):
        """
        Sets up the main data table, which contains general information
        about each file.
        """
        # First drop table
        if self.droptable:
            query = """DROP TABLE IF EXISTS `files`"""
            self.executeQuery(query)
        
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
        
        # Truncate table if not already dropped before
        if self.truncate and not self.droptable:
            query = """TRUNCATE `files`"""
            self.executeQuery(query)
        
    def setupMimeTypesTable(self):
        """
        Sets up the glue data table, this table contains which mime-types uses which modules.
        """
        # First drop table
        if self.droptable:
            query = """DROP TABLE IF EXISTS `supported_mimetypes`"""
            self.executeQuery(query)

        query="""CREATE TABLE IF NOT EXISTS `supported_mimetypes`
            (`mime_type` VARCHAR(512) NOT NULL PRIMARY KEY,
            INDEX USING HASH (`mime_type`),
            `modules` LONGTEXT)"""
        self.executeQuery(query)
        
        # Truncate table if not already dropped before
        if self.truncate and not self.droptable:
            query = """TRUNCATE `supported_mimetypes`"""
            self.executeQuery(query)

    def setupModuleTable(self,table,columns):
        """
        Sets up a specified table.

        table - The name of the table
        columns - A string with multiple column names and datatypes,
            separated by commas. Example:
            Summary:LONGSTRING, Index:SMALLINT
        """
        if not table or not columns:
            raise ValueError('Module table or columns missing.')
        
        # First drop table
        if self.droptable:
            query = """DROP TABLE IF EXISTS `"""+table+"""`"""
            self.executeQuery(query)
        
        query = """CREATE TABLE IF NOT EXISTS `"""+table+"""` (`hashid` BIGINT UNSIGNED NOT NULL, INDEX USING HASH (`hashid`)"""
        for items in columns.split(','):
            name,type = items.split(':')
            name = name.strip()
            type = type.strip()
            query += """,`"""+name+"""` """+type
        query += """, PRIMARY KEY(`hashid`));"""
        self.executeQuery(query)

        # Truncate table if not already dropped before
        if self.truncate and not self.droptable:
            query = """TRUNCATE `"""+table+"""`"""
            self.executeQuery(query)

    def store(self,table,hashid,columns,values):
        """
        Inserts data into the specified table (main table or module
        table).

        table - The name of the table
        hashid - The file's hash id
        columns - A tuple with the name of each column
        values - A tuple with the value for each column
        """
        if not table or not columns or not values:
            raise ValueError('Module table, columns or values missing.')
        query = """INSERT IGNORE INTO `"""+table+"""` (`hashid`"""
        for item in columns:
            query += ", `"+item+"`"
        query += """) VALUES ("""+str(hashid)
        values = self._replaceNoneValue(values)
        for item in values:
            query += ", '%s'"
        query += """);"""
        escaped = []
        for i in values:
            escaped.append(MySQLdb.escape_string(str(i)))
        escaped = tuple(escaped)
        escapedQuery = query%escaped
        escapedQuery = escapedQuery.replace(""" (, """,""" (""")
        escapedQuery = escapedQuery.replace("""'NULL'""","""NULL""")
        self.executeQuery(escapedQuery)
    
    def storeMimetypeValues(self,table,columns,values):
        """
        Inserts data into the specified table (supported_mimetypes).

        table - The name of the table
        columns - A tuple with the name of each column
        values - A tuple with the value for each column
        """
        if not table or not columns or not values:
            raise ValueError('supported_mimetypes table, columns or values missing.')
        query = """INSERT IGNORE INTO `"""+table+"""` ("""
        for item in columns:
            query += " `"+item+"`,"
        query += """) VALUES ("""
        values = self._replaceNoneValue(values)
        for item in values:
            query += " '%s',"
        query += """);"""
        escaped = []
        for i in values:
            escaped.append(MySQLdb.escape_string(str(i)))
        escaped = tuple(escaped)
        escapedQuery = query%escaped
        escapedQuery = escapedQuery.replace(""",)""",""")""")
        escapedQuery = escapedQuery.replace("""'NULL'""","""NULL""")
        self.executeQuery(escapedQuery)
        
    def _replaceNoneValue(self, values):
        """
        This methods replaces all None values to NULL
        """
        index = 0
        for value in values:
            if value is None:
                values[index] = "NULL"
            index += 1
        return values
