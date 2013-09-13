import libutil

def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import sys, pkg_resources, imp
   __file__ = libutil.get_library_path('tika', '_tika')
   __loader__ = None; del __bootstrap__, __loader__
   imp.load_dynamic(__name__,__file__)
__bootstrap__()
