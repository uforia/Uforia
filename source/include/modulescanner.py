#!/usr/bin/env python

import os, glob, imp

class Modules(object):
    def __init__(self,config,db):
        self.modules = {}
        self.modulelist = {}
        self.moduletotable = {}
        self.moduletabletocolumns = {}
        for major in os.listdir(config.MODULEDIR):
            for minor in os.listdir(config.MODULEDIR+major):
                mimetype = major+'/'+minor
                self.modulelist[mimetype] = glob.glob(config.MODULEDIR+mimetype+"/*.py")
                for modulepath in self.modulelist[mimetype]:
                    tableDef = False
                    with open(modulepath) as file:
                        for line in file:
                            if line.startswith("""#TABLE: """):
                                tableDef = True
                                columns = line.strip('\n').replace("""#TABLE: """,'')
                                modulename = modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','.')
                                tablename = modulepath[2:].strip(config.MODULEDIR).strip('.py').replace('/','_')
                                self.modules[modulename] = imp.load_source(modulename,modulepath)
                                self.moduletotable[modulename] = tablename
                                self.moduletabletocolumns[tablename] = columns.split(':')[0]
                                db.setupModuleTable(self.moduletotable[modulename],columns)
                                break
                    if not tableDef:
                        del self.modulelist[mimetype]
