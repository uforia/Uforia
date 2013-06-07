#!/usr/bin/env python

# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# Load basic Python modules
import os
import imp
import sys
import platform
import traceback
import site
import ctypes
import recursive
import hashlib

# Loading of Uforia modules is deferred until run() is called
config = None
File = None
magic = None
modules = None
database = None


def write_to_db(table, hashid, columns, values, db=None):
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
    db.store(table, hashid, columns, values)

    db.connection.commit()
    db.connection.close()


def write_to_mimetypes_table(table, columns, values, db=None):
    """
    Method that writes to database

    table - the database table
    columns - the database columns
    values - the values for in the columns
    db - Optionally use another database object
    """
    if db == None:
        db = database.Database(config)

    db.store_mimetype_values(table, columns, values)

    db.connection.commit()
    db.connection.close()


def file_scanner(dir, uforiamodules, rcontext):
    """
    Walks through the specified directory tree to find all files. Each
    file is passed through file_processor, which is called asynchronously
    through the multiprocessing pool (consumers).

    dir - The path to search
    uforiamodules - Loaded uforia modules, passed to file_processor
    """
    try:
        if config.DEBUG:
            print("Starting in directory " + dir + "...")
            print("Starting filescanner...")

        filelist = []
        for root, dirs, files in os.walk(dir, topdown=True, followlinks=False):
            for name in files:
                fullpath = os.path.join(root, name)
                filelist.append((fullpath, rcontext.hashid.value))
                rcontext.hashid.value += 1

        for item in filelist:
            file_processor(item, uforiamodules)
    except:
        traceback.print_exc(file=sys.stderr)
        raise


def invoke_modules(uforiamodules, hashid, file):
    """
    Loads all Uforia modules.
    Only modules that apply to the current MIME-type are loaded.
    The result of the module's process method will be put to the
    database.

    uforiamodules - The uforia module objects from modulescanner
    hashid - The hash id of the currently processed file
    file - The file currently being processed
    """
    modules = uforiamodules.get_modules_for_mimetype(file.mtype)
    nr_handlers = 0
    for module in modules:
        if module.is_mime_handler:
            nr_handlers += 1

    if nr_handlers == 0:
        if config.DEBUG:
            print "No modules found to handle MIME-type " + file.mtype + ", skipping additional file parsing..."
    else:
        try:
            modules = uforiamodules.get_modules_for_mimetype(file.mtype)
            if config.DEBUG:
                print "Setting up " + str(nr_handlers) + " module workers..."
            for module in modules:
                try:
                    # If module fails catch it's exception and continue running Uforia.
                    module.load_sources()
                    processresult = None
                    if module.is_mime_handler:
                        processresult = module.pymodule.process(file.fullpath, config, rcontext, columns=module.columnnames)
                    if processresult != None:
                        write_to_db(module.md5_tablename, hashid, module.columnnames, processresult)
                except:
                    traceback.print_exc(file=sys.stderr)
        except:
            traceback.print_exc(file=sys.stderr)
            raise


def file_processor(item, uforiamodules):
    """
    Process a file item and export its information to the database.
    Also calls invoke_modules() if modules are enabled in the
    configuration.

    item - Tuple containing the fullpath and hashid of the file
    uforiamodules - The uforia module objects from modulescanner
    """
    try:
        fullpath, hashid = item
        file = File.File(fullpath, config, magic)
        try:
            if config.DEBUG:
                print("Exporting basic hashes and metadata to database.")
            columns = ('fullpath', 'name', 'size', 'owner', 'group', 'perm', 'mtime', 'atime', 'ctime', 'md5', 'sha1', 'sha256', 'ftype', 'mtype', 'btype')
            if rcontext.spoofed_startdir != None:
                fullpath = rcontext.spoofed_startdir + os.path.sep + os.path.relpath(file.fullpath, config.STARTDIR)
            else:
                fullpath = file.fullpath
            values = (fullpath, file.name, file.size, file.owner, file.group, file.perm, file.mtime, file.atime, file.ctime, file.md5, file.sha1, file.sha256, file.ftype, file.mtype, file.btype)

            write_to_db('files', hashid, columns, values)
        except:
            traceback.print_exc(file=sys.stderr)
            raise
        if not config.ENABLEMODULES:
            if config.DEBUG:
                print("Additional module parsing disabled by config, skipping...")
        else:
            invoke_modules(uforiamodules, hashid, file)
    except:
        traceback.print_exc(file=sys.stderr)
        raise


def fill_mimetypes_table(uforiamodules):
    """
    Fills the supported_mimetypes table with all available mime-types
    """
    if config.DEBUG:
        print "Getting available mimetypes..."
    mime_types = uforiamodules.get_all_supported_mimetypes_with_modules()
    for mime_type in mime_types:
        write_to_mimetypes_table('supported_mimetypes', ["mime_type", "modules"], [mime_type, mime_types[mime_type]])


def run():
    """
    Starts Uforia.

    Sets up the database, modules, and then
    invokes the file_scanner.
    """

    print("Uforia starting...")

    db = database.Database(config)
    if not rcontext.is_recursive:
        db.setup_main_table()
        db.setup_mimetypes_table()

    if config.ENABLEMODULES:
        if config.DEBUG:
            print("Detecting available modules...")
        uforiamodules = modules.Modules(config, db, rcontext)
        if not rcontext.is_recursive:
            fill_mimetypes_table(uforiamodules)
    else:
        uforiamodules = ''
    if config.DEBUG:
        print("Starting producer...")
    if os.path.exists(config.STARTDIR):
        file_scanner(config.STARTDIR, uforiamodules, rcontext)
    else:
        print("The pathname " + config.STARTDIR + " does not exist, stopping...")
    print("\nUforia completed...\n")


class _Dummy(object):
    pass


def config_as_pickleable(config):
    """
    Converts config (which has the `module' type) to a pickleable object.
    """
    values = config.__dict__
    newConfig = _Dummy()
    for key, value in values.items():
        if not key.startswith('__'):
            setattr(newConfig, key, value)
    return newConfig


def setup_library_paths():
    """
    Setup the PATH environmental variable so that python libraries, .pyd, .so and
    .dll files can be loaded without intervention. This does not work for Linux
    shared object files loaded with ctypes.
    """
    architecture = 'x86_64' if ctypes.sizeof(ctypes.c_voidp) == 8 else 'x86'
    operatingSystem = platform.system()

    # Needs to be loaded first, otherwise system-wide libraries are preferred
    sys.path.insert(0, "./libraries")
    sys.path.append("./libraries/PIL/bin-{0}-{1}".format(architecture, operatingSystem))
    sys.path.append("./libraries/pysqlite/bin-{0}-{1}".format(architecture, operatingSystem))
    if platform.system() == 'Windows':
        # sys.path.append is not reliable for this thing
        os.environ['PATH'] += ";./libraries/windows-deps"

setup_library_paths()


# Fixes crash-on-exit bugs on Windows by loading it before libmagic
import libxmp

config = imp.load_source('config', 'include/default_config.py')
try:
    config = imp.load_source('config', 'include/config.py')
except:
    print("< WARNING! > Config file not found or not configured correctly, loading default config.")
File = imp.load_source('File', 'include/File.py')
magic = imp.load_source('magic', 'include/magic.py')
modules = imp.load_source('modulescanner', 'include/modulescanner.py')
database = imp.load_source(config.DBTYPE, config.DATABASEDIR + config.DBTYPE + ".py")

config = config_as_pickleable(config)
config.UFORIA_RUNNING_VERSION = 'Uforia_debug'
rcontext = recursive.RecursionContext()

if __name__ == "__main__":
    run()
