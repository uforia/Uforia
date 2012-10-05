#!/usr/bin/env python

# Load basic Python modules
import os, sys, re, time, multiprocessing, imp, glob

# Add loader paths to config files, support classes and database handlers
sys.path.append('./include')

# Load Uforia custom modules
import config, File, magic, modulescanner

class Uforia(object):
    def __init__(self):
        if config.DEBUG:
            print("Listing available modules for MIME types...")
        self.moduleScanner()
        if config.DEBUG:
            print("Initializing "+config.DBTYPE+" database connection...")
        self.databaseModule = imp.load_source(config.DBTYPE,config.DATABASEDIR+config.DBTYPE+".py")
        self.db = self.databaseModule.Database(config.DBHOST,config.DBUSER,config.DBPASS,config.DBNAME)
        if config.DEBUG:
            print("Setting up "+str(config.CONSUMERS)+" consumer(s)...")
        self.consumers=multiprocessing.Pool(processes=config.CONSUMERS)
        if config.DEBUG:
            print("Starting producer...")
        self.fileScanner(config.STARTDIR)

    def moduleScanner(self):
        if config.DEBUG:
            print("Starting in directory "+config.MODULEDIR+"...")
            print("Starting modulescanner...")
        self.modules=modulescanner.ModuleProxy(config.MODULEDIR)
        self.modulelist={}
        for major in os.listdir(config.MODULEDIR):
            for minor in os.listdir(config.MODULEDIR+major):
                mimetype=major+'/'+minor
                self.modulelist[mimetype]=glob.glob(config.MODULEDIR+mimetype+"/*.py")

    def fileScanner(self,dir):
        if config.DEBUG:
            print("Starting in directory "+config.STARTDIR+"...")
            print("Starting filescanner...")
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath=os.path.join(root,name)
                if config.DEBUG:
                    print("Added:",fullpath)
                self.consumers.apply_async(self.fileProcessor(fullpath))
    
    def fileProcessor(self,fullpath):
        self.file=File.File(fullpath,config.DEBUG)
        try:
	        if config.DEBUG:
	            print("Hashes and metadata exported to database.")
	        # TODO: Store the stuff in the database
        except:
            raise IOError('Error storing hashes, possible database problem.')
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
                    mod=self.modules
                    for target in s.split('.'):
                        try:
                            mod=getattr(mod,target)
                        except AttributeError:
                            pass
                    if config.DEBUG:
                        print("Called:",target,".process()")
                    f=self.modulepool.apply_async(getattr(mod,'process')(fullpath,1,'test',s))
            except:
                raise
					
if __name__ == "__main__":
    main=Uforia()
