#!/usr/bin/env python

# Load basic Python modules
import os, sys, re, time, multiprocessing, imp, curses, glob

# Load Uforia custom modules
try:
    config      = imp.load_source('config','include/config.py')
    File        = imp.load_source('File','include/File.py')
    magic       = imp.load_source('magic','include/magic.py')
    modules     = imp.load_source('modulescanner','include/modulescanner.py')
    database    = imp.load_source(config.DBTYPE,config.DATABASEDIR+config.DBTYPE+".py")
except:
    raise

def dbworker():
    db = database.Database(config)
    db.setupMainTable()
    while True:
        table,hashid,columns,values = dbqueue.get()
        db.store(table,hashid,columns,values)
        dbqueue.task_done()
    db.connection.commit()
    db.connection.close()

def run():
    print("Uforia starting...")
    if config.DEBUG:
        print("Initializing "+str(config.DBCONN)+" "+config.DBTYPE+" database worker thread(s)...")
    global dbqueue
    dbqueue = multiprocessing.JoinableQueue()
    for i in range(config.DBCONN):
        dbthread = multiprocessing.Process(target = dbworker)
        dbthread.daemon = True
        dbthread.start()
    global uforiamodules
    if config.ENABLEMODULES:
        if config.DEBUG:
            print("Detecting available modules...")
        db = database.Database(config)
        uforiamodules = modules.Modules(config,db)
        del db
    else:
        uforiamodules = '';
    if config.DEBUG:
        print("Setting up "+str(config.CONSUMERS)+" consumer(s)...")
    consumers = multiprocessing.Pool(processes=config.CONSUMERS)
    if config.DEBUG:
        print("Starting producer...")
    if os.path.exists(config.STARTDIR):
        fileScanner(config.STARTDIR,consumers)
    else:
        print("The pathname "+config.STARTDIR+" does not exist, stopping...")
    dbqueue.join()
    print("Uforia completed...")

def fileScanner(dir,consumers):
    if config.DEBUG:
        print("Starting in directory "+config.STARTDIR+"...")
        print("Starting filescanner...")
    hashid=1
    filelist=[]
    for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
        for name in files:
            fullpath=os.path.join(root,name)
            filelist.append((fullpath,hashid))
            hashid+=1;
    consumers.map_async(fileProcessor,filelist)
    consumers.close()
    consumers.join()

def fileProcessor(item):
    multiprocessing.current_process().daemon=False
    fullpath,hashid=item
    file=File.File(fullpath,config,magic)
    if config.OUTPUT:
        stdscr.addstr(0,0,"=== Uforia ===")
        stdscr.addstr(2,0,"Examining:")
        stdscr.addstr(2,20,str(fullpath))
        stdscr.clrtoeol()
        stdscr.refresh()
    try:
        if config.DEBUG:
            print("Exporting basic hashes and metadata to database.")
        columns = ('fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
        values = (file.fullpath, file.name, file.size, file.owner, file.group, file.perm, file.mtime, file.atime, file.ctime, file.md5, file.sha1, file.sha256, file.ftype, file.mtype, file.btype)
        dbqueue.put(('files',hashid,columns,values))
    except:
        raise
    if not config.ENABLEMODULES:
        if config.DEBUG:
            print("Additional module parsing disabled by config, skipping...")
    else:
        if file.mtype not in uforiamodules.modulelist:
            if config.DEBUG:
                print("No modules found to handle MIME-type "+file.mtype+", skipping additional file parsing...")
        else:
            try:
                if config.DEBUG:
                    print("Setting up "+str(config.MODULES)+" module workers...")
                handlers = []
                for handler in uforiamodules.modulelist[file.mtype]:
                    handlers.append(handler[2:].strip(config.MODULEDIR).strip('.py').replace('/','.'))
                for s in handlers:
                    moduletable = uforiamodules.moduletotable[s]
                    modulecolumns = uforiamodules.moduletabletocolumns[uforiamodules.moduletotable[s]]
                    dbqueue.put(uforiamodules.modules[s].process(moduletable,hashid,modulecolumns,file.fullpath))
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
