# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import ctypes
import platform

PLATFORM_SHARED_LIBRARY_EXTENSIONS = {
    'Windows': '.dll',
    'Linux': '.so',
    'Darwin': '.dylib'}

def _get_arch():
    if ctypes.sizeof(ctypes.c_voidp) == 8:
        return 'x86_64'
    else:
        return 'x86'


def load_library(foldername, filename, apiversion=None):
    """
    Returns the correct version of the shared library/DLL with ctypes
    based on the OS version or architecture.
    foldername - The name of the library folder where the shared library
    should be loaded
    filename - The name of the actual shared library file, without an
    extension
    apiversion - Optionally adds an extension for the shared object api
    version on Linux (e.g. libfoo.so.5)
    """
    architecture = _get_arch()

    os = platform.system()
    extension = PLATFORM_SHARED_LIBRARY_EXTENSIONS[os]
    if apiversion != None and os != 'Windows':
        extension += '.' + str(apiversion)

    path = './libraries/{foldername}/bin-{arch}-{os}/{filename}{ext}'.format(
        foldername=foldername,
        arch=architecture,
        os=os,
        filename=filename,
        ext=extension)
    return ctypes.cdll.LoadLibrary(path)


def get_executable(foldername, filename):
    """
    Returns path to the correct version of a platform-specific
    executable file.
    foldername - The name of the folder where the binaries reside in
    filename - The name of the executable
    """
    architecture = _get_arch()
    os = platform.system()
    extension = ".exe" if os == "Windows" else ""

    return "./libraries/{foldername}/bin-{arch}-{os}/{filename}{ext}".format(
        foldername=foldername,
        arch=architecture,
        os=os,
        filename=filename,
        ext=extension)
