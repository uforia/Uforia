#!/usr/bin/env python

# Load basic Python modules
import os, multiprocessing, imp, curses, sys, platform, traceback, site, subprocess, ctypes

ENVIRONMENTAL_VARIABLES_LOADED = '--_envset' in sys.argv

# Load Uforia custom modules
if ENVIRONMENTAL_VARIABLES_LOADED:
    try:
        config      = imp.load_source('config','include/config.py')
        File        = imp.load_source('File','include/File.py')
        magic       = imp.load_source('magic','include/magic.py')
        modules     = imp.load_source('modulescanner','include/modulescanner.py')
        database    = imp.load_source(config.DBTYPE,config.DATABASEDIR+config.DBTYPE+".py")
    except:
        raise

def dbworker(dbqueue, db=None):
    """
    Receives new argument lists from the database queue and writes them
    to the database. The worker will continue until it receives a table
    with the name "No more tasks" (the sentinel) in the argument list. Upon
    receiving the sentinel, it will send a commit to write out all
    outstanding I/O to the database. 

    dbqueue - The database queue, a multiprocessing.JoinableQueue
    db - Optionally use another database object
    """
    if db == None:
        db = database.Database(config)
    db.setupMainTable()
    while True:
        table,hashid,columns,values = dbqueue.get()
        if table != "No more tasks":
            db.store(table,hashid,columns,values)
            dbqueue.task_done()
        else:
            break
    db.connection.commit()
    dbqueue.task_done()
    db.connection.close()

def monitorworker(monitorqueue):
    """
    Starts the monitor display for the curses console.

    monitorqueue - The multiprocessing.JoinableQueue that emits the
        currently examined file
    """
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)

    while True:
        val = monitorqueue.get()
        if val != None:
            stdscr.clear()
            stdscr.addstr(0,0,"=== Uforia ===")
            stdscr.addstr(2,0,"Examining:")
            stdscr.addstr(2,20,str(val))
            if config.DEBUG:
                stdscr.addstr(24,0,"Warning: console output will be severely mangled with debug enabled.")
            stdscr.clrtoeol()
            stdscr.refresh()
            monitorqueue.task_done()
        else:
            break

    monitorqueue.task_done()
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()

def fileScanner(dir,consumers,dbqueue,monitorqueue,uforiamodules):
    """
    Walks through the specified directory tree to find all files. Each
    file is passed through fileProcessor, which is called asynchronously
    through the multiprocessing pool (consumers).

    dir - The path to search
    consumers - The multiprocessing.Pool which will carry out the
        file processing task
    dbqueue - The database queue, passed to fileProcessor
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
            consumers.apply_async(fileProcessor,args=(item,dbqueue,monitorqueue,uforiamodules))
        consumers.close()
        consumers.join()
    except:
        traceback.print_exc(file=sys.stderr)
        raise

def invokeModules(dbqueue, uforiamodules, hashid, file):
    """
    Loads all Uforia modules in the current process and invokes them.
    Only modules that apply to the current MIME-type are loaded.
    The result of the module's process method will be put to the
    database queue.

    dbqueue - The database queue, a multiprocessing.JoinableQueue
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
                    processresult = module.pymodule.process(file.fullpath, columns=module.columnnames)
                    if processresult != None:
                        dbqueue.put((module.tablename, hashid, module.columnnames, processresult))
        except:
            traceback.print_exc(file = sys.stderr)
            raise

def fileProcessor(item,dbqueue,monitorqueue,uforiamodules):
    """
    Process a file item and export its information to the database
    queue. Also calls invokeModules() if modules are enabled in the
    configuration.

    item - Tuple containing the fullpath and hashid of the file
    dbqueue - The database queue, a multiprocessing.JoinableQueue
    monitorqueue - The monitoring queue to show information about the
        current file
    uforiamodules - The uforia module objects from modulescanner
    """
    try:
        multiprocessing.current_process().daemon=False
        fullpath,hashid=item
        file=File.File(fullpath,config,magic)
        if config.OUTPUT:
            monitorqueue.put(fullpath)
        try:
            if config.DEBUG:
                print("Exporting basic hashes and metadata to database.")
            columns = ('fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
            values = (file.fullpath, file.name, file.size, file.owner, file.group, file.perm, file.mtime, file.atime, file.ctime, file.md5, file.sha1, file.sha256, file.ftype, file.mtype, file.btype)
            dbqueue.put(('files',hashid,columns,values))
        except:
            traceback.print_exc(file=sys.stderr)
            raise
        if not config.ENABLEMODULES:
            if config.DEBUG:
                print("Additional module parsing disabled by config, skipping...")
        else:
            invokeModules(dbqueue, uforiamodules, hashid, file)
    except:
        traceback.print_exc(file=sys.stderr)
        raise

def run():
    """
    Starts Uforia.

    Sets up the database, modules, all background processes and then
    invokes the fileScanner.
    """
    print("Uforia starting...")

    if config.DEBUG:
        print("Initializing "+str(config.DBCONN)+" "+config.DBTYPE+" database worker thread(s)...")

    manager = multiprocessing.Manager()
    dbqueue = manager.JoinableQueue()
    dbworkers = []
    for i in range(config.DBCONN):
        dbworkers.append(multiprocessing.Process(target = dbworker, args = (dbqueue,)))
        dbworkers[i].daemon = True
        dbworkers[i].start()
    if config.ENABLEMODULES:
        if config.DEBUG:
            print("Detecting available modules...")
        db = database.Database(config)
        uforiamodules = modules.Modules(config,db)
        del db
    else:
        uforiamodules = '';
    monitorqueue = None
    if config.OUTPUT:
        monitorqueue = manager.JoinableQueue()
        monitorthread = multiprocessing.Process(target = monitorworker, args = (monitorqueue,))
        monitorthread.daemon = True
        monitorthread.start()
    if config.DEBUG:
        print("Setting up "+str(config.CONSUMERS)+" consumer(s)...")
    consumers = multiprocessing.Pool(processes=config.CONSUMERS)
    if config.DEBUG:
        print("Starting producer...")
    if os.path.exists(config.STARTDIR):
        fileScanner(config.STARTDIR,consumers,dbqueue,monitorqueue,uforiamodules)
    else:
        print("The pathname "+config.STARTDIR+" does not exist, stopping...")
    for i in range(config.DBCONN):
        dbqueue.put(('No more tasks','','',''))
    dbqueue.join()
    if config.OUTPUT:
        monitorqueue.put(None)
        monitorqueue.join()
    print("\nUforia completed...\n")

if __name__ == "__main__":
    architecture = 'x86_64' if ctypes.sizeof(ctypes.c_voidp)==8 else 'x86'
    operatingSystem = platform.system()

    # Reloads current file with additional so/dll import paths
    if not ENVIRONMENTAL_VARIABLES_LOADED:
        if platform.system() == 'Windows':
            os.environ['PATH'] = './libraries/windows-deps;./libraries/libxmp/bin-%s-%s;%s' % (architecture, operatingSystem, os.environ['PATH'])
        else:
            os.environ['LD_LIBRARY_PATH'] = './libraries/libxmp/bin-%s-%s' % (architecture, operatingSystem)

        subprocess.check_call(
            [sys.executable, __file__, '--_envset'])
    else:
        # Site dir for third-party library imports
        site.addsitedir("./libraries")

        # Contrary to XMP toolkit, PIL uses importable shared object binaries (.so/.pyd);
        # so we only need to add them to sitelib, changing environmental vars is unnecessary
        site.addsitedir("./libraries/PIL/bin-%s-%s" % (architecture, operatingSystem))
        run()
