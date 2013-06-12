Creating additional modules
==========================
The creation of a new module is quite simple. First, determine the MIME-type the module is written for. Then create a new python file with its path equal to the name of the MIME-type (relative to the module folder). So to support the `application/x-hg2g` MIME-type, we would have to create a new python file in `source/modules/application/x-hg2g/`. The creation of additional folders might be necessary. Do not forget to add an (empty) `__init__.py` file to all new folders. The name of the python module should be descriptive but has no special requirements.

The newly created module will require a `process` function and a comment defining the columns of the database table. The function should return a list or tuple containing the parsed information. A bare-bones example:
```
# TABLE: name:LONGTEXT, value:INT

def process(fullpath, config, rcontext, columns=None):
    return ("Answer to the Ultimate Question of Life, the Universe, and Everything", 42)
```

The arguments to the process function are, in order:

* **fullpath**: Contains the path to the to-be-examined file
* **config**: The Uforia setting values
* **rcontext**: Contains values needed to run Uforia recursively, irrelevant for most use cases
* **columns**: A list with the names of the database columns (the same as defined in the comments)

Take a look at other modules for common usage patterns.

