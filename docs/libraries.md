Libraries
======
Apart from [mysqldb][] and [pdcurses][] (Windows-specific), every library that Uforia depends on is included in the `libraries` subfolder inside the source tree. The rationale for this is to be able to effortlessly deploy Uforia as stand-alone application. Furthermore, it assures that the correct versions of all libraries are installed (altough PIP incorporates [functionality][pip_requirements] for this particular concern.)

Including additional libraries
------
To include additional libraries, simply copy the python package to the `libraries` subfolder. Make sure all licensing and authorship information is preserved. If you are installing a pure python library, no additional steps need to be performed. The `PATH` environmental variable will automatically include the `libraries` subfolder, so you can import them as usual.

Conventions for loading shared object files (*nix) or dynamic link libraries (Windows)
------
Many libraries depend on certain binary modules written in C or C++, therefore they need to be imported with ctypes or use the python binary extension module format, `.so/.pyd`. The latter are simply shared objects or dll's with a certain [convention][binary_modules].

As Uforia, unconventionally, needs to load these libraries within its own source tree (rather than inside `/usr/lib` or `C:\Windows\System32`), some work is needed to actually make them load correctly.

Modules using ctypes should be patched to use the `load_library` function from `libutil.py`. Modules using python binary extensions should have their directory path added to the `PATH` environmental variable. See the source of **libxmp** for the former and **PIL** for the latter.

The directory where the binary files should reside is `libraries/<library name>/bin-<architecture>-<platform>`, e.g. `libraries/PIL/bin-x86_64-Linux` or `libraries/PIL/bin-x86-Windows`. Currently we only provide compiled libraries for 32 and 64 bit Linux versions and 32-bit Python for Windows.

Instructions for compiling library binaries
------
### Linux/OS X
Install build-essentials/XCode/etc. and perform the `./configure` and `make` commands, simple as that. Note that some libraries might require other dependencies. [Exempi][], for example, requires [zlib][] and [expat][].

### Windows
This is a little bit more complicated. Since many open source libraries are written using autotools, Visual Studio can not be used to compile them. It will be required to download any MinGW distribution and MSYS. You can use the [Official MinGW Installer][official_installer], [TDM-GCC][] or [Mingw Distro][mingw_dist]. Depending on the distrubution you've chosen, installing MSYS seperately might still be needed. Make sure to install a recent version, as many libraries don't work with old autotools (which should be included with MSYS).

By booting up the MSYS console you should be able the same `./configure` and `make` commands inside the folder where the library has been extracted. You might have some weird error that complains about not being able to compile a DLL. In that case, try passing `lt_cv_deplibs_check_method=pass_all`.

Note that some libraries (such as [exempi][]) do not cleanly compile on Windows and might need some additional tweaking and/or patching of header files. Some experience with autotools, C or C++ is recommended in order to be able to compile these libraries.

[mysqldb]: https://pypi.python.org/pypi/MySQL-python/1.2.4
[pdcurses]: http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
[pip_requirements]: http://www.pip-installer.org/en/latest/requirements.html
[binary_modules]: http://docs.python.org/2/extending/building.html
[exempi]: http://www.ohloh.net/p/exempi
[zlib]: http://zlib.net/
[expat]: http://expat.sourceforge.net/
[official_installer]: http://sourceforge.net/projects/mingw/files/Installer/mingw-get-inst/mingw-get-inst-20120426/
[tdm-gcc]: http://tdm-gcc.tdragon.net/
[mingw_dist]: http://nuwen.net/mingw.html
