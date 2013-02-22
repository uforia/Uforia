#!/usr/bin/env python

import os, glob, imp

class Modules(object):
    """
    A class for the dynamic loading of Uforia modules.

    The format for defining module columns is as follows (this should
    be inside a normal python comment):
    #TABLE: <column name>:<data type>, <column name>:<data type>,...
    Example:
    #TABLE: Title:LONGTEXT, Subject:LONGTEXT

    Each defined module should have a process() function which accepts
    a path to the file to analyze. It should return a tuple with the
    data for each column.
    """
    def __init__(self,config,db):
        """
        Initializes a Modules object, which will check the configuration
        for valid module path(s) and add the necessary columns defined
        by the modules to the database.

        config - The uforia configuration object
        db - The uforia database object
        """
        self.modules = {}
        self.modulelist = {}
        self.moduletotable = {}
        self.moduletabletocolumns = {}
        self.modulepaths = {}
        for mimetype in os.listdir(config.MODULEDIR):
            self.modulelist[mimetype] = glob.glob(config.MODULEDIR+mimetype+"/*.py")
            for modulepath in self.modulelist[mimetype]:
                tableDef = False
                with open(modulepath) as file:
                    for line in file:
                        if line.startswith("""#TABLE: """):
                            tableDef = True
                            columnline = line.strip('\n').replace("""#TABLE: """,'')
                            modulename = modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','.')
                            tablename = modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','_')
                            self.modulepaths[modulename] = modulepath
                            self.moduletotable[modulename] = tablename
                            columns = []
                            for columnelement in columnline.split(','):
                                column = columnelement.split(':')[0]
                                columns.append(column)
                            self.moduletabletocolumns[tablename] = columns
                            db.setupModuleTable(self.moduletotable[modulename],columnline)
                            break

                if not tableDef:
                    del self.modulelist[mimetype]

    def loadModules(self):
        """
        Because the result of imp.load_source can't be shared between processes, each process
        using a module should call this function to actually load its sources and put the modules
        in the modules attribute.
        """
        for modulename, modulepath in self.modulepaths.items():
            self.modules[modulename] = imp.load_source(modulename,modulepath)

