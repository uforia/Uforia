import os
top=os.getcwd()
for root, dirs, files in os.walk(top, topdown=False):
	for name in files:
		print os.path.join(root,name)
	for name in dirs:
		x=os.path.join(root,name)
		print x
