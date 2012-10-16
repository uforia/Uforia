#!/usr/bin/env python

# Load basic Python modules
import os, sys, re, time, multiprocessing, imp, glob, curses

# Add loader paths to config files, support classes and database handlers
sys.path.append('./include')
sys.path.append('./databases')

# Load Uforia custom modules
import config, File, magic

def run():
    if config.DEBUG:
        print("Initializing "+config.DBTYPE+" database connection...")
    databaseModule = imp.load_source(config.DBTYPE,config.DATABASEDIR+config.DBTYPE+".py")
    global db
    db = databaseModule.Database(config)
    if config.ENABLEMODULES:
        if config.DEBUG:
            print("Listing available modules for MIME types...")
        moduleScanner()
    if config.DEBUG:
        print("Setting up "+str(config.CONSUMERS)+" consumer(s)...")
    consumers=multiprocessing.Pool(processes=config.CONSUMERS)
    if config.DEBUG:
        print("Starting producer...")
    fileScanner(config.STARTDIR,consumers)

def moduleScanner():
    if config.DEBUG:
       print("Starting in directory "+config.MODULEDIR+"...")
    modules={}
    modulelist={}
    tabletocolumns={}
    moduletotable={}
    for major in os.listdir(config.MODULEDIR):
        for minor in os.listdir(config.MODULEDIR+major):
            mimetype=major+'/'+minor
            modulelist[mimetype]=glob.glob(config.MODULEDIR+mimetype+"/*.py")
            for modulepath in modulelist[mimetype]:
                with open(modulepath) as file:
                    for line in file:
                        if line.startswith("""#TABLE: """):
                            columns=line.strip('\n').replace("""#TABLE: """,'')
                            modulename=modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','.')
                            tablename=modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','_')
                            modules[modulename]=imp.load_source(modulename,modulepath)
                            moduletotable[modulename]=tablename
                            tabletocolumns[tablename]=columns.split(':')[0]
                            db.setup(moduletotable[modulename],columns)

def fileScanner(dir,consumers):
    if config.DEBUG:
        print("Starting in directory "+config.STARTDIR+"...")
        print("Starting filescanner...")
    hashid=1
    filelist=[]
    for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
        totalfiles=len(files)
        for name in files:
            fullpath=os.path.join(root,name)
            filelist.append((fullpath,hashid,totalfiles))
            hashid+=1;
    consumers.map_async(fileProcessor, filelist)
    consumers.close()
    consumers.join()

def fileProcessor(item):
    fullpath=item[0]
    hashid=item[1]
    totalfiles=item[2]
    file=File.File(fullpath,config)
    if config.OUTPUT:
        stdscr.addstr(0,0,"=== Uforia ===")
        stdscr.addstr(2,0,"Examining:\t"+str(fullpath))
        stdscr.clrtoeol()
        stdscr.refresh()
    try:
        if config.DEBUG:
            print("Exporting basic hashes and metadata to database.")
        columns=('hashid','fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
        values=(hashid,file.fullpath, file.name, file.size, file.owner, file.group, file.perm, file.mtime, file.atime, file.ctime, file.md5, file.sha1, file.sha256, file.ftype, file.mtype, file.btype)
        db.store('files','',columns,values)
    except:
        raise
    if not config.ENABLEMODULES:
        if config.DEBUG:
            print("Additional module parsing disabled by config, skipping...")
    else:
        if file.mtype not in modulelist:
            if config.DEBUG:
                print("No modules found to handle MIME-type "+file.mtype+", skipping additional file parsing...")
        else:
   	        lasthashid=db.findhash((file.fullpath,))
    	        if not lasthashid:
	                raise
        try:
            if config.DEBUG:
                print("Setting up "+str(config.MODULES)+" module workers...")
            modulepool=multiprocessing.Pool(processes=config.MODULES)
            handlers=[]
            for handler in modulelist[file.mtype]:
                handlers.append(handler[2:].strip(config.MODULEDIR).strip('.py').replace('/','.'))
            for s in handlers:
                func=getattr(modules[s],'process')
                table=moduletotable[s]
                columns=tabletocolumns[moduletotable[s]]
                args=(db,table,lasthashid,columns,file.fullpath)
                modulepool.map_async(func,*args)
        except:
            raise
					
if __name__ == "__main__":
    try:
        if config.OUTPUT:
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(1)
        run()
    finally:
        if config.OUTPUT:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
