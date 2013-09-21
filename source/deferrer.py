# Copyright (C) 2013 Hogeschool van Amsterdam

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

def _get_arch_linux():
    if ctypes.sizeof(ctypes.c_voidp) == 8:
        return 'amd64'
    else:
        return 'i386'


def _do_linux_setup():
    javapathcmd = "readlink -f $(which java)"
    proc = subprocess.Popen(javapathcmd, shell=True, stdout=subprocess.PIPE)
    out = proc.communicate()

    if proc.returncode:
        print "WARNING: Java not found. Modules using JVM will not function."
    else:
        linuxarch = _get_arch_linux()

        javapath = os.path.abspath(out[0] + "/../../../")
        javalibpath = os.path.join(javapath, "jre/lib/" + linuxarch)
        javaserverpath = os.path.join(javalibpath, "server")

        os.environ['UFORIA_WRAPPER'] = "YES"
        if not 'LD_LIBRARY_PATH' in os.environ:
            os.environ['LD_LIBRARY_PATH'] = ""

        os.environ['LD_LIBRARY_PATH'] += ":" + javalibpath + ":" + javaserverpath


def run_uforia_deferred(runfunction):
    """
    Sets up LD_LIBRARY_PATH to make libraries built with JCC find the correct JVM path.
    For this to work, the python process /must/ be restarted.
    """
    if 'UFORIA_WRAPPER' in os.environ:
        runfunction()
    else:
        if platform.system() == 'Linux':
            _do_linux_setup()
            subprocess.call([sys.executable] + sys.argv)
