import hashlib
import threading
#filepath='/home/carlo/test/aap'
class md5calc:
	def md5hash(self, filepath, fh, m, threading.Thread):
		def __init__(self, fh, m, filepath):
			fh = open(filepath, 'rb')
			m = hashlib.md5()
			threading.Thread.__init__(self)
		
		while True:
			data = fh.read(8192)
			if not data:
				break
			m.update(data)
		return m.hexdigest()
	
#print 'md5 checksum of file is', md5hash(filepath)
