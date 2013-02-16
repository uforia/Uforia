#!/usr/bin/env python

import os, glob, imp

class Modules(object):
    def __init__(self,config,db):
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

    def load_modules(self):
        """
        Because the result of imp.load_source can't be shared between processes, each process
        using a module should call this function to actually load its sources and put the modules
        in the modules attribute.
        """
        for modulename, modulepath in self.modulepaths.items():
            self.modules[modulename] = imp.load_source(modulename,modulepath)
        
