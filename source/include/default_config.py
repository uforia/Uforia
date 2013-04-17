#!/usr/bin/env python

class Default_config:
    
    # Enable debug output. Prints lots of information about internal workings.
    # Note: Debug output is very noisy and should not be used in production.
    DEBUG = False
    
    # Should Uforia show a progress indicator? (Might slow down things...!)
    OUTPUT = False
    
    # From which directory should Uforia start to scan?
    # Example: STARTDIR = '/home/user/' 
    STARTDIR = '/home/TESTDATA/'
    
    # Should Uforia attempt to detect and run additional modules for each
    # of the fond files/filetypes? If so, where should Uforia find the
    # modules to handle those files?
    # Note: You should not normally have to modify this!
    # Example: ENABLEMODULES = True
    # Example: MODULEDIR = './modules/'
    ENABLEMODULES = False
    MODULEDIR = './modules/'
    
    # Should Uforia modules use the libxmp library for optional XMP support?
    ENABLEXMP = True
    
    # Database configuration. The name should match the handler providing
    # the appropriate Database class with setupMainTable() and setupTable()
    # and store() methods. See one of the provided database handlers for more
    # information.
    # Example: DBTYPE = 'mysql'
    DATABASEDIR = './databases/'
    DBTYPE = 'mysql'
    DBHOST = 'localhost'
    DBUSER = 'uforia'
    DBPASS = 'uforia'
    DBNAME = 'uforia'
    
    # How many simultaneous database connections should we use to handle
    # the queue of SQL queries? Warning: setting this too high can overload
    # or hamper database performance
    DBCONN = 2
    
    # Should Uforia DROP any existing tables? Setting this to False
    # can be useful when you want to add additional evidence items on an
    # already-examined filesystem
    DROPTABLE = True
    
    # Should Uforia TRUNCATE any existing tables? Setting this to False
    # can be useful when you want to add additional evidence items on an
    # already-examined filesystem
    TRUNCATE = True
    
    # How many processes should be parsing files at the same time?
    # Note: This is a tradeoff between CPU power and disk I/O. More workers
    # means higher CPU utilization, but disk I/O might become a limiting factor.
    # Conversely: less workers might mean optimal disk I/O, but your CPU might
    # be sitting idle...
    # Example: CONSUMERS = 2
    CONSUMERS = 2
    
    # ADVANCED CONFIGURATION, FOR EXPERTS ONLY
    
    # Tune the filesystem block reads
    # Example: CHUNKSIZE = 65536
    CHUNKSIZE = 65536
    
    # Maximum number of database connection attempts before giving up
    DBRETRY = 5
    
    # Location of the magic file (needs only be supplied on Windows machines)
    # Example (Windows):  MAGICFILE = 'C:/Program Files (x86)/GnuWin32/share/misc/magic'
    # Example (Linux):    MAGICFILE = None
    MAGICFILE = './share/magic.mgc'
