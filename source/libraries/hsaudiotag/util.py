# Created By: Virgil Dupras
# Created On: 2010-12-20
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
#
# This software is licensed under the "BSD" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.hardcoded.net/licenses/bsd_license

def open_if_filename(file_or_path, mode=u'rb'):
    u"""
    file_or_path can be either a string or a file-like object.
    if it is a string, a file will be opened with mode.
    Returns a tuple (file, should_be_closed).
    """
    if isinstance(file_or_path, basestring):
        return (open(file_or_path, mode), True)
    else:
        return (file_or_path, False)

class FileOrPath(object):
    def __init__(self, file_or_path, mode=u'rb'):
        self.file_or_path = file_or_path
        self.mode = mode
        self.mustclose = False
        self.fp = None

    def __enter__(self):
        self.fp, self.mustclose = open_if_filename(self.file_or_path, self.mode)
        return self.fp

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fp and self.mustclose:
            self.fp.close()


def cond(condition, true_value, false_value):
    u"""Return true_value if condition is true, and false_value otherwise.
    """
    return true_value if condition else false_value

def tryint(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
