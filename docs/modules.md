Creating additional modules
==========================
The creation of a new module is quite simple. First, determine the MIME-type the module is written for. Then create a new python file with its path equal to the name of the MIME-type (relative to the module folder). So to support the `application/x-hg2g` MIME-type, we would have to create a new python file in `source/modules/application/x-hg2g/`. The creation of additional folders might be necessary. Do not forget to add an (empty) `__init__.py` file to all new folders. The name of the python module should be descriptive but has no special requirements.

The newly created module will require a `process` function and a comment defining the columns of the database table. The function should return a list or tuple containing the parsed information. A bare-bones example:
```
# TABLE: name:LONGTEXT, value:INT

def process(file, config, rcontext, columns=None):
    return ("Answer to the Ultimate Question of Life, the Universe, and Everything", 42)
```

The arguments to the process function are, in order:

* **file**: Uforia file object, contains amongst others the path to the to-be-examined file (.fullpath) and mime-type of the file
* **config**: The Uforia setting values
* **rcontext**: Contains values needed to run Uforia recursively, irrelevant for most use cases
* **columns**: A list with the names of the database columns (the same as defined in the comments)

Take a look at other modules for common usage patterns.

### Recursive modules
In the ../source folder is a file called recursive. With this class you can recursively loop through i.e. archives to retrieve the documents inside, including their metadata. The first step to do is get a library or program to extract data from the archive, you can configure this in the `config.py` file inside `source/include`, the the example below on how to do this. Also configure a temporary extractdir in the config.
```
# In which directory should Uforia extract all archive files?
# If set to None, a temporary directory is created inside the users default
# temporary direcotory.
# Example: EXTRACTDIR = '/home/ARCHIVES/'
EXTRACTDIR = None

# Which tool should Uforia use to extract RAR files?
# Default: UNRAR_TOOL = "unrar"
# Example: UNRAR_TOOL = "C:\Program Files\WinRAR\WinRAR.exe"
UNRAR_TOOL = "unrar"
```

After that step you're ready to write a recursive module. You first need to import the recursive file and library for the corresponding archive. Extract the data in a temporary dir, and after that delete the temporary dir again. Below is an example of the rar-module.
```
import rarfilelib.rarfile as rarfile
import recursive

def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    # Try to parse RAR data
    try:
        # Set to full path of unrar.exe if it is not in PATH
        rarfile.UNRAR_TOOL = config.UNRAR_TOOL

        rar = rarfile.RarFile(fullpath)
        
    # Try to extract the content of the rar file.
        try:
            # Create a temporary directory
            tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)

            # Extract the rar file
            rar.extractall(tmpdir)

            recursive.call_uforia_recursive(config, rcontext, tmpdir, fullpath)

            # Close the rar file
            rar.close()
        except:
            traceback.print_exc(file=sys.stderr)
        
        # Delete the temporary directory, proceed even if it causes
        # an error
        try:
            pass
            shutil.rmtree(tmpdir)
        except:
            traceback.print_exc(file=sys.stderr)
            
```
The rest of the module is basically the same as any other module. For more modules which use the recursive class, check the archive modules.