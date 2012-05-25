import os
from md5 import md5calc


top=os.getcwd()
c=md5calc()


#top is the top directory of the search, in this case the current
#working directory where the script is being executed
def find(top):
	for root, dirs, files in os.walk(top, topdown=False):
#walk through the directory structures; topdown=false
#doesnt allow modifying the directory listings on the spot
		for name in files:
			filepath=os.path.join(root,name)
			print "file found: ", os.path.join(root,name), c.md5hash( md5hash(), () )
			print "current top is: ", top
			#adds the location to the filenames, printing full path
		for name in dirs:
			top=os.path.join(root,name)
			#full directory path is set as new source dir
			print "directory found: ", os.path.join(root,name)
			print "current top is: ", 
			#find(top)
			#function is launched again from the found directories

find(top)






