#!/usr/bin/env python

import imp,os

class ModuleCache(dict):
    pass

class ModuleProxy(object):
    def __init__(self, path, cache=None):
        if isinstance(path, basestring):
            self._path = [path, ]
        else:
            self._path = path
        self._cache = cache
        if self._cache is None:
            self._cache = ModuleCache()

    def __call__(self, *args, **kwargs):
        pathname = os.path.join(*self._path[:-1]) + ".py"
        module = self._cache.get(pathname, None)
        if module is None:
            if not os.path.isfile(pathname):
                raise AttributeError("%s does not exist" % (pathname, ))
            module = imp.load_source(self._path[-2], os.path.join(*self._path[:-1]) + ".py")
            self._cache[pathname] = module
        getattr(module, self._path[-1])(*args, **kwargs)

    def __getattr__(self, name):
        return ModuleProxy(self._path + [name, ], self._cache)

#mod = ModuleProxy("modules")
#l = ['text.plain.plaintextreader']
#for s in l:
#    for e in s.split('.'):
#        mod = getattr(mod,e)
#    f = getattr(mod,'process')('testasd')
