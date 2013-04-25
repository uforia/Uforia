#!/usr/bin/env python

# Load basic Python modules
import os, imp, sys, platform, traceback, site, ctypes

class Uforia_debug:
    def __init__(self, override_config = None):        
        self.setupLibraryPaths()
        
        # Import is needed for xmp.
        import libxmp
        
        # Load Uforia custom modules    
        if override_config == None:
            self.config      = imp.load_source('config','include/default_config.py')
            try:
                self.config      = imp.load_source('config','include/config.py')
            except:
                print("< WARNING! > Config file not found or not configured correctly, loading default config.")
        else:
            self.config = override_config
            
        self.File        = imp.load_source('File','include/File.py')
        self.magic       = imp.load_source('magic','include/magic.py')
        self.modules     = imp.load_source('modulescanner','include/modulescanner.py')
        self.database    = imp.load_source(self.config.DBTYPE,self.config.DATABASEDIR+self.config.DBTYPE+".py")

        self.run()
        
    def writeToDB(self, table, hashid, columns, values, db=None):
        """
        Method that writes to database
    
        table - the database table
        hashid - files primary key
        columns - the database columns
        values - the values for in the columns
        db - Optionally use another database object
        """
        if db == None:
            db = self.database.Database(self.config)
        db.store(table,hashid,columns,values)
    
        db.connection.commit()
        db.connection.close()
    
    def writeToMimeTypesTable(self, table, columns, values, db=None):
        """
        Method that writes to database
    
        table - the database table
        columns - the database columns
        values - the values for in the columns
        db - Optionally use another database object
        """
        if db == None:
            db = self.database.Database(self.config)
            
        db.storeMimetypeValues(table,columns,values)
    
        db.connection.commit()
        db.connection.close()
    
    def fileScanner(self, dir,uforiamodules):
        """
        Walks through the specified directory tree to find all files. Each
        file is passed through fileProcessor, which is called asynchronously
        through the multiprocessing pool (consumers).
    
        dir - The path to search
        uforiamodules - Loaded uforia modules, passed to fileProcessor
        """
        try:
            if self.config.DEBUG:
                print("Starting in directory "+dir+"...")
                print("Starting filescanner...")
            import random
            hashid=random.randint(0, 1000000) # temporary workaround
            filelist=[]
            for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
                for name in files:
                    fullpath = os.path.join(root,name)
                    filelist.append((fullpath,hashid))
                    hashid += 1;
            for item in filelist:
                self.fileProcessor(item,uforiamodules)
        except:
            traceback.print_exc(file=sys.stderr)
            raise
    
    def invokeModules(self, uforiamodules, hashid, file):
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
            if self.config.DEBUG:
                print "No modules found to handle MIME-type " + file.mtype + ", skipping additional file parsing..."
        else:
            try:
                modules = uforiamodules.getModulesForMimetype(file.mtype)
                if self.config.DEBUG:
                    print "Setting up " + str(nrHandlers) + " module workers..."
                for module in modules:
                    try:
                        # If module fails catch it's exception and continue running Uforia.
                        module.loadSources()
                        processresult = None
                        if module.isMimeHandler:
                            processresult = module.pymodule.process(file.fullpath, self.config, columns=module.columnnames)
                        if processresult != None:
                            self.writeToDB(module.tablename, hashid, module.columnnames, processresult)
                    except:
                        traceback.print_exc(file = sys.stderr)
            except:
                traceback.print_exc(file = sys.stderr)
                raise
    
    def fileProcessor(self, item,uforiamodules):
        """
        Process a file item and export its information to the database.
        Also calls invokeModules() if modules are enabled in the
        configuration.
    
        item - Tuple containing the fullpath and hashid of the file
        uforiamodules - The uforia module objects from modulescanner
        """
        try:
            fullpath,hashid=item
            file = self.File.File(fullpath,self.config,self.magic)
            try:
                if self.config.DEBUG:
                    print("Exporting basic hashes and metadata to database.")
                columns = ('fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
                if self.config.SPOOFSTARTDIR != None:
                    fullpath = self.config.SPOOFSTARTDIR + os.path.sep + os.path.relpath(file.fullpath, self.config.STARTDIR)
                else:
                    fullpath = file.fullpath
                values = (fullpath, file.name, file.size, file.owner, file.group, file.perm, file.mtime, file.atime, file.ctime, file.md5, file.sha1, file.sha256, file.ftype, file.mtype, file.btype)
    
                self.writeToDB('files',hashid,columns,values)
            except:
                traceback.print_exc(file=sys.stderr)
                raise
            if not self.config.ENABLEMODULES:
                if self.config.DEBUG:
                    print("Additional module parsing disabled by config, skipping...")
            else:
                self.invokeModules(uforiamodules, hashid, file)
        except:
            traceback.print_exc(file=sys.stderr)
            raise
        
    def fillMimeTypesTable(self, uforiamodules):
        """
        Fills the supported_mimetypes table with all available mime-types
        """
        if self.config.DEBUG:
            print "Getting available mimetypes..."
        mime_types = uforiamodules.getAllSupportedMimeTypesWithModules()
        for mime_type in mime_types:
            self.writeToMimeTypesTable('supported_mimetypes', ["mime_type", "modules"],[mime_type, mime_types[mime_type]])
    
    def run(self):
        """
        Starts Uforia.
    
        Sets up the database, modules, and then
        invokes the fileScanner.
        """
    
        print("Uforia starting...")
        
        db = self.database.Database(self.config)
        db.setupMainTable()
        db.setupMimeTypesTable()
        
        if self.config.ENABLEMODULES:
            if self.config.DEBUG:
                print("Detecting available modules...")
            uforiamodules = self.modules.Modules(self.config,db)
            self.fillMimeTypesTable(uforiamodules)
        else:
            uforiamodules = '';
        if self.config.DEBUG:
            print("Starting producer...")
        if os.path.exists(self.config.STARTDIR):
            self.fileScanner(self.config.STARTDIR,uforiamodules)
        else:
            print("The pathname "+self.config.STARTDIR+" does not exist, stopping...")
        print("\nUforia completed...\n")
    
    def setupLibraryPaths(self):
        """
        Setup the PATH environmental variable so that python libraries, .pyd, .so and
        .dll files can be loaded without intervention. This does not work for Linux
        shared object files loaded with ctypes.
        """
        architecture = 'x86_64' if ctypes.sizeof(ctypes.c_voidp)==8 else 'x86'
        operatingSystem = platform.system()
    
        sys.path.insert(0, "./libraries")
        sys.path.append("./libraries/PIL/bin-{0}-{1}".format(architecture, operatingSystem))
        if platform.system() == 'Windows':
            # sys.path.append is not reliable for this thing
            os.environ['PATH'] += ";./libraries/windows-deps"

def start(override_config = None):
    Uforia_debug(override_config)
    
if __name__ == "__main__":
    start()
