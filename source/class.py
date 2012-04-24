import os
from md5 import md5calc
import magic
from hash import filetomd5
top=os.getcwd()
#c=filetomd5()


#top is the top directory of the search, in this case the current
#working directory where the script is being executed
def find(top):
	for root, dirs, files in os.walk(top, topdown=False):
#walk through the directory structures; topdown=false
#doesnt allow modifying the directory listings on the spot
		for name in files:
			filepath=os.path.join(root,name)
			ftype=magic.from_file(filepath)
			mtype=magic.from_file(filepath, mime=True)
			btype=magic.from_buffer(open(filepath).read(1024))
			print "file found: ", os.path.join(root,name), "\n hashes:", filetomd5(filepath), "\n file magic:", ftype, mtype, btype
			print "current directory is is: ", top
			#adds the location to the filenames, printing full path
		for name in dirs:
			top=os.path.join(root,name)
			#full directory path is set as new source dir
			print "directory found: ", os.path.join(root,name)
			print "current directory is: ", 
			#find(top)
			#function is launched again from the found directories
find(top)
