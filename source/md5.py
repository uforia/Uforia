import hashlib

#filepath='/home/carlo/test/aap'
class md5calc:
	def md5hash(self, filepath):
		fh = open(filepath, 'rb')
		m = hashlib.md5()
		while True:
			data = fh.read(8192)
			if not data:
				break
			m.update(data)
		return m.hexdigest()
	
#print 'md5 checksum of file is', md5hash(filepath)

