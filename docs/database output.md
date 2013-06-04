Database ouput
======
The Uforia database consists out of a large amount of tables. The database has a layered structure by making use of junction tables. All of this will be explained in the preceeding parts of this manual.

Hashed table names
-----
The first thing you'll notice are the table names. Most of the tables, except the tables *supported_mimetypes* and *files*, have a hashed table which is hashed by MD5. The reason why the tablenames are hashed is because the length of the table names could exceed the allowed maximum length. How to know which table is which will be explained in the next paragraph.

Database structure
-----
In the design of the Uforia database we use junction tables for each mimetype, i.e. for the mimetype *image/jpeg* etc. we have a table which contains all *image* files with their basic metadata, like the MAC times. This *image* table also includes the other image mimetypes. The same situation is also applicable to *video*.
There is also a table called *supported_mimetypes*, as mentioned in the first paragraph the table names are hashed. In this table you will see all mimetypes and their belonging module names, behind that you'll see the hashed table name for that mimetype. That way you can search for the corresponding table.

Table content
-----
Each table has different content. The content depends on which metadata can be extracted from the certain file, because each file has a different amount of data the amount of columns per table also differ.
