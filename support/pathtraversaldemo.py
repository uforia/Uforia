#!/usr/bin/env python

import os

startdir = "."
filter = ['./Uforia/.git']

for root,subFolders,files in os.walk(startdir):
	for path in filter:
		if path in root:
			print "Deze directory slaan we over:",root
			continue
		else:
			for file in files:
				entry = os.path.join(root,file)
				print "Filter not matched:",entry
