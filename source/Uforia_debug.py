#!/usr/bin/env python

# Load basic Python modules
import os, imp, sys, platform, traceback, site, ctypes

# Loading of Uforia modules is deferred until run() is called
config      = None
File        = None
magic       = None
modules     = None
database    = None

def writeToDB(table, hashid, columns, values, db=None):
    """
    Method that writes to database

    table - the database table
    hashid - files primary key
    columns - the database columns
    values - the values for in the columns
    db - Optionally use another database object
    """
    if db == None:
        db = database.Database(config)
    db.store(table,hashid,columns,values)

    db.connection.commit()
    db.connection.close()

def writeToMimeTypesTable(table, columns, values, db=None):
    """
    Method that writes to database

    table - the database table
    columns - the database columns
    values - the values for in the columns
    db - Optionally use another database object
    """
    if db == None:
        db = database.Database(config)
        
    db.storeMimetypeValues(table,columns,values)

    db.connection.commit()
    db.connection.close()

def fileScanner(dir,uforiamodules):
    """
    Walks through the specified directory tree to find all files. Each
    file is passed through fileProcessor, which is called asynchronously
    through the multiprocessing pool (consumers).

    dir - The path to search
    uforiamodules - Loaded uforia modules, passed to fileProcessor
    """
    try:
        if config.DEBUG:
            print("Starting in directory "+dir+"...")
            print("Starting filescanner...")
        hashid=1
        filelist=[]
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath = os.path.join(root,name)
                filelist.append((fullpath,hashid))
                hashid += 1;
        for item in filelist:
            fileProcessor(item,uforiamodules)
    except:
        traceback.print_exc(file=sys.stderr)
        raise

def invokeModules(uforiamodules, hashid, file):
    """
    Loads all Uforia modules.
    Only modules that apply to the current MIME-type are loaded.
    The result of the module's process method will be put to the
    database.

    uforiamodules - The uforia module objects from modulescanner
    hashid - The hash id of the currently processed file
    file - The file currently being processed
    """
    modules = uforiamodules.getModulesForMimetype(file.mtype)
    nrHandlers = 0
    for module in modules:
        if module.isMimeHandler:
            nrHandlers+=1

    if nrHandlers == 0:
        if config.DEBUG:
            print "No modules found to handle MIME-type " + file.mtype + ", skipping additional file parsing..."
    else:
        try:
            modules = uforiamodules.getModulesForMimetype(file.mtype)
            if config.DEBUG:
                print "Setting up " + str(nrHandlers) + " module workers..."
            for module in modules:
                module.loadSources()
                if module.isMimeHandler:
                    processresult = module.pymodule.process(file.fullpath, config, columns=module.columnnames)
                    if processresult != None:
                        writeToDB(module.tablename, hashid, module.columnnames, processresult)
        except:
            traceback.print_exc(file = sys.stderr)
            raise

def fileProcessor(item,uforiamodules):
    """
    Process a file item and export its information to the database.
    Also calls invokeModules() if modules are enabled in the
    configuration.

    item - Tuple containing the fullpath and hashid of the file
    uforiamodules - The uforia module objects from modulescanner
    """
    try:
        fullpath,hashid=item
        file=File.File(fullpath,config,magic)
        try:
            if config.DEBUG:
                print("Exporting basic hashes and metadata to database.")
            columns = ('fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
            values = (file.fullpath, file.name, file.size, file.owner, file.group, file.perm, file.mtime, file.atime, file.ctime, file.md5, file.sha1, file.sha256, file.ftype, file.mtype, file.btype)
            writeToDB('files',hashid,columns,values)
        except:
            traceback.print_exc(file=sys.stderr)
            raise
        if not config.ENABLEMODULES:
            if config.DEBUG:
                print("Additional module parsing disabled by config, skipping...")
        else:
            invokeModules(uforiamodules, hashid, file)
    except:
        traceback.print_exc(file=sys.stderr)
        raise
    
def fillMimeTypesTable(uforiamodules):
    """
    Fills the supported_mimetypes table with all available mime-types
    """
    if config.DEBUG:
        print "Getting available mimetypes..."
    mime_types = uforiamodules.getAllSupportedMimeTypesWithModules()
    for mime_type in mime_types:
        writeToMimeTypesTable('supported_mimetypes', ["mime_type", "modules"],[mime_type, mime_types[mime_type]])

def run():
    """
    Starts Uforia.

    Sets up the database, modules, and then
    invokes the fileScanner.
    """

    print("Uforia starting...")

    db = database.Database(config)
    db.setupMainTable()
    db.setupMimeTypesTable()

    if config.ENABLEMODULES:
        if config.DEBUG:
            print("Detecting available modules...")
        uforiamodules = modules.Modules(config,db)
        fillMimeTypesTable(uforiamodules)
    else:
        uforiamodules = '';
    if config.DEBUG:
        print("Starting producer...")
    if os.path.exists(config.STARTDIR):
        fileScanner(config.STARTDIR,uforiamodules)
    else:
        print("The pathname "+config.STARTDIR+" does not exist, stopping...")
    print("\nUforia completed...\n")

def setupLibraryPaths():
    """
    Setup the PATH environmental variable so that python libraries, .pyd, .so and
    .dll files can be loaded without intervention. This does not work for Linux
    shared object files loaded with ctypes.
    """
    architecture = 'x86_64' if ctypes.sizeof(ctypes.c_voidp)==8 else 'x86'
    operatingSystem = platform.system()

    sys.path.append("./libraries")
    sys.path.append("./libraries/PIL/bin-{0}-{1}".format(architecture, operatingSystem))
    if platform.system() == 'Windows':
        # sys.path.append is not reliable for this thing
        os.environ['PATH'] += ";./libraries/windows-deps"

if __name__ == "__main__":
    setupLibraryPaths()

    # Load Uforia custom modules
    import libxmp
    
    # Try to get user config file, if it is not found or not configured correctly use the default.
    try:
        config      = imp.load_source('config','include/config.py').Config
    except (IOError, AttributeError):
        print("< WARNING! > Config file not found or not configured correctly, loading default config.")
        config      = imp.load_source('config','include/default_config.py').Default_config
    
    File        = imp.load_source('File','include/File.py')
    magic       = imp.load_source('magic','include/magic.py')
    modules     = imp.load_source('modulescanner','include/modulescanner.py')
    database    = imp.load_source(config.DBTYPE,config.DATABASEDIR+config.DBTYPE+".py")

    run()
