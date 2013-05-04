'''
Created on 17 apr. 2013

@author: marcin
'''
import ctypes
import platform

PLATFORM_SHARED_LIBRARY_EXTENSIONS = {
    'Windows': '.dll',
    'Linux': '.so',
    'Darwin': '.dylib'}


def loadLibrary(foldername, filename, apiversion=None):
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
    if ctypes.sizeof(ctypes.c_voidp) == 8:
        architecture = 'x86_64'
    else:
        architecture = 'x86'

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
