#!/usr/bin/env python

# Load basic Python modules
import os, sys, re, time, multiprocessing, imp, glob

# Add loader paths to config files, support classes and database handlers
sys.path.append('./include')

# Load Uforia custom modules
import config, File, magic

class Uforia(object):
    def __init__(self):
        if config.DEBUG:
            print("Initializing "+config.DBTYPE+" database connection...")
        self.databaseModule = imp.load_source(config.DBTYPE,config.DATABASEDIR+config.DBTYPE+".py")
        self.db = self.databaseModule.Database(config)
        if config.DEBUG:
            print("Listing available modules for MIME types...")
        self.moduleScanner()
        if config.DEBUG:
            print("Setting up "+str(config.CONSUMERS)+" consumer(s)...")
        self.consumers=multiprocessing.Pool(processes=config.CONSUMERS)
        if config.DEBUG:
            print("Starting producer...")
        self.fileScanner(config.STARTDIR)

    def moduleScanner(self):
        if config.DEBUG:
            print("Starting in directory "+config.MODULEDIR+"...")
        self.modules={}
        self.modulelist={}
        self.tabletocolumns={}
        self.moduletotable={}
        for major in os.listdir(config.MODULEDIR):
            for minor in os.listdir(config.MODULEDIR+major):
                mimetype=major+'/'+minor
                self.modulelist[mimetype]=glob.glob(config.MODULEDIR+mimetype+"/*.py")
                for modulepath in self.modulelist[mimetype]:
                    with open(modulepath) as file:
                        for line in file:
                            if line.startswith("""#TABLE: """):
                                columns=line.strip('\n').replace("""#TABLE: """,'')
                                modulename=modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','.')
                                tablename=modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','_')
                                self.modules[modulename]=imp.load_source(modulename,modulepath)
                                self.moduletotable[modulename]=tablename
                                self.tabletocolumns[tablename]=columns.split(':')[0]
                                self.db.setup(self.moduletotable[modulename],columns)

    def fileScanner(self,dir):
        if config.DEBUG:
            print("Starting in directory "+config.STARTDIR+"...")
            print("Starting filescanner...")
        self.hashid=1
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath=os.path.join(root,name)
                if config.DEBUG:
                    print("Added:",fullpath)
                self.consumers.apply_async(self.fileProcessor(fullpath,self.hashid))
                self.hashid+=1;
    
    def fileProcessor(self,fullpath,hashid):
        print "Examining:",fullpath
        self.file=File.File(fullpath,config.DEBUG)
        try:
	        if config.DEBUG:
	            print("Exporting basic hashes and metadata to database.")
	        columns=('hashid','fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
	        values=(hashid,self.file.fullpath, self.file.name, self.file.size, self.file.owner, self.file.group, self.file.perm, self.file.mtime, self.file.atime, self.file.ctime, self.file.md5, self.file.sha1, self.file.sha256, self.file.ftype, self.file.mtype, self.file.btype)
	        self.db.store('files','',columns,values)
	        lasthashid=self.db.findhash((self.file.fullpath,))
	        if not lasthashid:
	            raise
        except:
            raise
        if self.file.mtype not in self.modulelist:
            if config.DEBUG:
                print("No modules found to handle MIME-type "+self.file.mtype+", skipping additional file parsing...")
        else:
            try:
                if config.DEBUG:
                    print("Setting up "+str(config.MODULES)+" module workers...")
                self.modulepool=multiprocessing.Pool(processes=config.MODULES)
                handlers=[]
                for handler in self.modulelist[self.file.mtype]:
                    handlers.append(handler[2:].strip(config.MODULEDIR).strip('.py').replace('/','.'))
                for s in handlers:
                    func=getattr(self.modules[s],'process')
                    table=self.moduletotable[s]
                    columns=self.tabletocolumns[self.moduletotable[s]]
                    args=(self.db,table,lasthashid,columns,self.file.fullpath)
                    x=self.modulepool.apply_async(func(*args))
            except:
                raise
					
if __name__ == "__main__":
    main=Uforia()
