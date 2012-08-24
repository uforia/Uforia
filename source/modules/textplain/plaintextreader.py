#!/usr/bin/env python

import sys

# if arguments are given;
if (len(sys.argv) > 1):
	print "arguments passed: ", sys.argv[1:]
	# print all arguments, contents = contents of the file in argument
	contents = open(sys.argv[1], 'r').read()
	print contents
