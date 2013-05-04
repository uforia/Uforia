#!/usr/bin/env python

import os, imp, warnings

class Module:
    """
    Represents a single Uforia module file. This might be a handler
    for MIME types or a __init__.py file.
    """
    def __init__(self, path, name, mimetype=None, isGlobal=False, asMimeHandler=False):
        self.path = path
        self.name = name
        self.isGlobal = isGlobal
        self.mimetype = mimetype
        self.isMimeHandler = False
        self.tablename = ""
        self.columndefinition = ""
        self.columnnames = []
        self.pymodule = None
        self.__loadHandler()

    def __loadHandler(self):
        """
        Parses the table information inside a MIME handler module file.
        """
        with open(self.path) as file:
            for line in file:
                if line.startswith("""# TABLE: """):
                    self.columndefinition = line.strip('\n').replace("""# TABLE: """, '')
                    self.tablename = self.name.replace('.', '_')
                    for columnelement in self.columndefinition.split(','):
                        column = columnelement.split(':')[0].strip()
                        self.columnnames.append(column)

                    self.isMimeHandler = True

    def loadSources(self):
        """
        Because the result of imp.load_source can't be shared between processes, each process
        using a module should call this function to actually load its sources.
        """
        self.pymodule = imp.load_source(self.name, self.path)

class Modules:
    """
    A class for the dynamic loading of Uforia modules.

    The format for defining module columns is as follows (this should
    be inside a normal python comment):
    #TABLE: <column name>:<data type>, <column name>:<data type>,
    Example:
    #TABLE: Title:LONGTEXT, Subject:LONGTEXT

    Each defined MIME type handler should have a process() function
    which accepts a path to the file to analyze. It should return a
    tuple with the data for each column.
    """
    def __init__(self, config, db):
        self.modules = []
        self.__setupModules(config, db)

    def getModulesForMimetype(self, mimetype):
        """
        Returns all modules that apply to the given mimetype.
        """
        modules = []
        for module in self.modules:
            if module.isGlobal or module.mimetype == mimetype or (module.mimetype and mimetype.startswith(module.mimetype)):
                modules.append(module)
        return modules
    
    def getAllSupportedMimeTypesWithModules(self):
        """
        Returns all mime-types which Uforia supports with modules.
        """
    
        # init dictionary and list
        mime_types_with_columns = {}
        mime_types = []
        
        # First get all mime-types
        for module in self.modules:
            if (not module.isGlobal and not "__init__.py" in module.path):  # Global module is for each mime-type so ingnore it.
                if not module.mimetype in mime_types:  # If key not already exists, append to the list with mime-types
                    mime_types.append(module.mimetype)
        
        # Then get all columns for a mime-type
        for mime_type in mime_types:
            modules = []
            for module in self.modules:
                if (not module.isGlobal and not "__init__.py" in module.path):  # Global module is for each mime-type so ingnore it.
                    if module.mimetype == mime_type or (module.mimetype and mime_type.startswith(module.mimetype)):
                        modules.append(module.tablename)
                        
            mime_types_with_columns[mime_type] = modules
        
        del mime_types
        return mime_types_with_columns

    def __setupModules(self, config, db):
        """
        Loads all modules in the modules directory, including subdirectories
        and top-level modules.
        config - The uforia configuration object
        db - The uforia database object
        """
        DEPTH_ROOT = 0
        DEPTH_TYPE = 1
        DEPTH_SUBTYPE = 2

        for root, subFolders, files in os.walk("modules"):
            nicepath = os.path.relpath(root, "modules")
            fullpath = root

            if nicepath == '.':
                depth = DEPTH_ROOT
            else:
                depth = nicepath.count(os.path.sep) + 1

            if depth > DEPTH_SUBTYPE:
                warnings.warn("sub-subdirectory in module (%s) ignored." % nicepath)

            modulenamebase = nicepath.replace(os.path.sep, '.')
            mimetype = nicepath.replace(os.path.sep, '/')

            if depth != DEPTH_ROOT:
                # Each folder should except root have an __init__.py, otherwise the
                # directory name be assigned as a module.
                if not "__init__.py" in files:
                    warnings.warn("__init__.py not found in module folder '%s'." % nicepath)
                    continue

                modulepath = fullpath + os.path.sep + "__init__.py"
                module = Module(modulepath, modulenamebase, mimetype)
                self.modules.append(module)

            # Now load each handler .py file
            for file in files:
                modulenameend, extension = os.path.splitext(file)
                if extension.lower() == ".py":
                    isInit = file == "__init__.py"
                    modulepath = fullpath + os.path.sep + file
                    modulename = None
                    if isInit:
                        modulename = modulenamebase
                    elif depth == DEPTH_ROOT:
                        modulename = modulenameend
                    else:
                        modulename = modulenamebase + '.' + modulenameend

                    module = Module(modulepath, modulename, mimetype, isGlobal=(depth == DEPTH_ROOT), asMimeHandler=not isInit)
                    if module.isMimeHandler and not config.RECURSIVE:
                        db.setupModuleTable(module.tablename, module.columndefinition)

                    self.modules.append(module)
