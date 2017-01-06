# Copyright (C) 2013-2015 A. Eijkhoudt and others

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import sys
import platform
import subprocess
import platform
import ctypes

def _find_executable(execname, path=None):
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)

    if os.path.isfile(execname):
        return execname
    else:
        for p in paths:
            f = os.path.join(p, execname)
            if os.path.isfile(f):
                return f
    return None


def _get_arch_linux():
    if ctypes.sizeof(ctypes.c_voidp) == 8:
        return 'amd64'
    else:
        return 'i386'


def _do_linux_setup():
    # Replacing failed use of readlink via a shell process to a pythonic solution
    javaexec = _find_executable('java')
    if not javaexec:
        print "WARNING: Java not found. Modules using JVM will not function."
    else:
        javaexecrealpath = os.path.realpath(javaexec)
        javapath = os.path.dirname(javaexecrealpath) + '/../../'
        javapath = os.path.realpath(javapath)

        linuxarch = _get_arch_linux()

        javalibpath = os.path.join(javapath, "jre/lib/" + linuxarch)
        javaserverpath = os.path.join(javalibpath, "server")

        if not 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] = javalibpath + ":" + javaserverpath
        else:
            os.environ['LD_LIBRARY_PATH'] += ":" + javalibpath + ":" + javaserverpath

        os.environ['LD_LIBRARY_PATH'] += ":./libraries/PIL/bin-x86_64-Linux:./libraries/PIL/bin-x86-Linux"

def _do_win32_setup():
    import _winreg

    # Find Java path in registry
    KEYPATH = 'SOFTWARE\\JavaSoft\\Java Runtime Environment'

    try:
        hkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, KEYPATH)
    except WindowsError:
        print "WARNING: Java not found. Modules using JVM will not function."
        return

    try:
        i = 0
        while 1:
            lastkeyname = _winreg.EnumKey(hkey, i)
            i += 1
    except WindowsError:
        pass
    javahomekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, KEYPATH + '\\' + lastkeyname)
    javahomepath = _winreg.QueryValueEx(javahomekey, 'JavaHome')[0]

    _winreg.CloseKey(hkey)
    _winreg.CloseKey(javahomekey)

    # Put the values in the environment
    os.environ['JAVA_HOME'] = javahomepath
    os.environ['PATH'] += ';{0}/bin;{0}/bin/client'.format(javahomepath)

    # Fix heap error on windows
    os.environ['_JAVA_OPTIONS'] = "-Xmx128M"


def _linux_run(runfunction):
    if '_UFORIA_WRAPPER' in os.environ:
        runfunction()
    else:
        os.environ['_UFORIA_WRAPPER'] = 'YES'
        _do_linux_setup()
        subprocess.call([sys.executable] + sys.argv)

def _windows_run(runfunction):
    _do_win32_setup()
    runfunction()


def setup_and_run(runfunction):
    """
    On Windows: set up correct Java JRE paths and options
    On Linux: sets up LD_LIBRARY_PATH to make libraries built with JCC find
    the correct JVM path. For this to work, the python process /must/ be
    restarted.

    """
    if platform.system() == 'Windows':
        _windows_run(runfunction)
    else:
        _linux_run(runfunction)
