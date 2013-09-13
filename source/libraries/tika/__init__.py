import os, _tika

#_tika = libutil.load_library('tika', '_tika')
__dir__ = os.path.abspath(os.path.dirname(__file__))

class JavaError(Exception):
  def getJavaException(self):
    return self.args[0]
  def __str__(self):
    writer = StringWriter()
    self.getJavaException().printStackTrace(PrintWriter(writer))
    return "\n".join((super(JavaError, self).__str__(), "    Java stacktrace:", str(writer)))

class InvalidArgsError(Exception):
  pass

_tika._set_exception_types(JavaError, InvalidArgsError)

VERSION = "1.3"
CLASSPATH = [os.path.join(__dir__, "org.eclipse.osgi.jar"), os.path.join(__dir__, "log4j.properties.jar"), os.path.join(__dir__, "tika-app-1.3.jar"), os.path.join(__dir__, "tika-parsers-1.3.jar"), os.path.join(__dir__, "tika-core-1.3.jar")]
CLASSPATH = os.pathsep.join(CLASSPATH)
_tika.CLASSPATH = CLASSPATH
_tika._set_function_self(_tika.initVM, _tika)

from _tika import *
