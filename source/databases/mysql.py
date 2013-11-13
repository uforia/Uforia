# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import warnings
import time
import sys
import traceback
import json
import base64
import MySQLdb


class Database(object):
    """
    This is a MySQL implementation of Uforia's data storage facility.
    """

    def __init__(self, config):
        """
        Initializes a MySQL database connection using the specified Uforia
        configuration.

        config - The uforia configuration object
        """
        if (not config.DBHOST or not config.DBUSER
                or not config.DBPASS or not config.DBNAME):
            raise ValueError("""Cannot initialize a database
                            connection without valid credentials.""")
        else:
            hostname = config.DBHOST
            username = config.DBUSER
            password = config.DBPASS
            database = config.DBNAME
            self.truncate = config.TRUNCATE
            self.droptable = config.DROPTABLE
            self.connection = None
            attempts = 0
            retries = config.DBRETRY
        while not self.connection:
            try:
                attempts += 1
                self.connection = MySQLdb.connect(host=hostname,
                                                  user=username,
                                                  passwd=password,
                                                  db=database,
                                                  charset='utf8',
                                                  use_unicode=True)
            except MySQLdb.OperationalError, e:
                print("Could not connect to the MySQL server: " + str(e))
                print("Sleeping for 3 seconds...")
                time.sleep(3)
                if attempts > retries:
                    print("The MySQL server didn't respond after "
                          + str(retries) +
                          """ requests; you might be flooding it
                          with connections.""")
                    print("""Consider raising the maximum amount of
                            connections on your MySQL server or lower
                            the amount of concurrent Uforia threads!""")
                    traceback.print_exc(file=sys.stderr)
                    break
        try:
            self.cursor = self.connection.cursor()
        except:
            traceback.print_exc(file=sys.stderr)

    def execute_query(self, query, params=None):
        """
        Executes a query (which should have no data to return).

        query - The query string
        """
        try:
            warnings.filterwarnings('ignore', category=self.connection.Warning)
            self.cursor.execute(query, params)
            warnings.resetwarnings()
        except:
            traceback.print_exc(file=sys.stderr)

    def setup_main_table(self):
        """
        Sets up the main data table, which contains general information
        about each file.
        """
        # First drop table
        if self.droptable:
            query = """DROP TABLE IF EXISTS `files`"""
            self.execute_query(query)

        query = """CREATE TABLE IF NOT EXISTS `files`
            (`hashid` BIGINT UNSIGNED NOT NULL PRIMARY KEY,
            INDEX USING HASH (`hashid`),
            `fullpath` LONGTEXT,
            `name` LONGTEXT,
            `size` BIGINT,
            `owner` INT,
            `group` INT,
            `perm` LONGTEXT,
            `mtime` LONGTEXT,
            `atime` LONGTEXT,
            `ctime` LONGTEXT,
            `md5` VARCHAR(32),
            `sha1` VARCHAR(40),
            `sha256` VARCHAR(64),
            `ftype` LONGTEXT,
            `mtype` LONGTEXT,
            `btype` LONGTEXT)"""
        self.execute_query(query)

        # Truncate table if not already dropped before
        if self.truncate and not self.droptable:
            query = """TRUNCATE `files`"""
            self.execute_query(query)

    def setup_mimetypes_table(self):
        """
        Sets up the glue data table,
        this table contains which mime-types uses which modules.
        """
        # First drop table
        if self.droptable:
            query = """DROP TABLE IF EXISTS `supported_mimetypes`"""
            self.execute_query(query)

        query = "CREATE TABLE IF NOT EXISTS `supported_mimetypes`\
            (`mime_type` VARCHAR(255) NOT NULL PRIMARY KEY,\
            INDEX USING HASH (`mime_type`),\
            `modules` LONGTEXT)"
        self.execute_query(query)

        # Truncate table if not already dropped before
        if self.truncate and not self.droptable:
            query = """TRUNCATE `supported_mimetypes`"""
            self.execute_query(query)

    def setup_module_table(self, table, columns):
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
            query = """DROP TABLE IF EXISTS `""" + table + """`"""
            self.execute_query(query)

        query = """CREATE TABLE IF NOT EXISTS `""" + table + "`\
                (`hashid` BIGINT UNSIGNED NOT NULL,\
                INDEX USING HASH (`hashid`)"
        for items in columns.split(','):
            name, type = items.split(':')
            name = name.strip()
            type = type.strip()
            query += """,`""" + name + """` """ + type
        query += """, PRIMARY KEY(`hashid`));"""
        self.execute_query(query)

        # Truncate table if not already dropped before
        if self.truncate and not self.droptable:
            query = """TRUNCATE `""" + table + """`"""
            self.execute_query(query)

    def store(self, table, hashid, columns, values):
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
        query = """INSERT IGNORE INTO `""" + table + """` (`hashid`"""
        for item in columns:
            query += ", `" + item + "`"
        query += """) VALUES (""" + str(hashid)
        values = self._replace_values(values)
        for item in values:
            query += ", %s"
        query += """);"""
        params = []
        for i in values:
            # To prevent unicode strings being converted to ascii 
            if isinstance(i, unicode):
                string = i
            else:
                string = str(i) 
            params.append(string)
        query = query.replace(""" (, """, """ (""")
        query = query.replace("""'NULL'""", """NULL""")
        self.execute_query(query, params)

    def store_mimetype_values(self, table, columns, values):
        """
        Inserts data into the specified table (supported_mimetypes).

        table - The name of the table
        columns - A tuple with the name of each column
        values - A tuple with the value for each column
        """
        if not table or not columns or not values:
            raise ValueError("""supported_mimetypes table,
                                columns or values missing.""")
        query = """INSERT IGNORE INTO `""" + table + """` ("""
        for item in columns:
            query += " `" + item + "`,"
        query += """) VALUES ("""
        values = self._replace_values(values)
        for item in values:
            query += " '%s',"
        query += """);"""
        escaped = []
        for i in values:
            escaped.append(MySQLdb.escape_string(str(i)))
        escaped = tuple(escaped)
        escapedQuery = query % escaped
        escapedQuery = escapedQuery.replace(""",)""", """)""")
        escapedQuery = escapedQuery.replace("""'NULL'""", """NULL""")
        self.execute_query(escapedQuery)

    def _replace_values(self, database_values):
        """
        This methods replaces all None database_values to NULL
        And converts a dictionary, list and tuple to JSON.
        """
        index = 0

        # Loop through all values
        for column_value in database_values:

            # If value is None replace it with NULL.
            if column_value is None:
                database_values[index] = "NULL"

            # If value is a dictionary, list or tuple convert it to JSON.
            if (isinstance(column_value, dict) or
                isinstance(column_value, list) or
                isinstance(column_value, tuple)):
                database_values = self._convert_to_JSON(database_values,
                                                         column_value, index)

            index += 1
        return database_values

    def _convert_to_JSON(self, database_values, column_value, index):
        """
        This method converts the database values to JSON
        """
        try:
            # Try to convert to JSON.
            database_values[index] = json.dumps(column_value)

        # If JSON can't decode it to UTF8, try to encode it to base64
        except UnicodeDecodeError:
            try:
                # Try encoding for a dictionary format
                for key, dictValue in column_value.items():
                    column_value[key] = base64.b64encode(dictValue)

                # Try to convert to JSON.
                database_values[index] = json.dumps(column_value)

            except:
                try:
                    # Try encoding for list format
                    new_column_value = (column_value[0],
                                        base64.b64encode(column_value[1]))

                    # Try to convert to JSON.
                    database_values[index] = json.dumps(new_column_value)

                except:
                    try:
                        # Try encoding for list in a list format
                        new_column_value = (column_value[0][0],
                                            base64.b64encode
                                            (column_value[0][1]))

                        # Try to convert to JSON.
                        database_values[index] = json.dumps(new_column_value)
                    except:
                        pass

        # If JSON doesn't know the type, try to parse it to a normal list
        except TypeError:
            try:
                # Try parsing to a list
                for key, dictValue in column_value.items():
                    column_value[key] = dictValue.tolist()

                # Try to convert to JSON.
                database_values[index] = json.dumps(column_value)
            except:
                pass

        # Return parsed JSON data
        return database_values
