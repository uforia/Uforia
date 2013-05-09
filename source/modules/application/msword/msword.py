#!/usr/bin/env python

# TABLE: title:LONGTEXT, subject:LONGTEXT, author:LONGTEXT, changedBy:LONGTEXT, revision:INT, createdOn:DATE, changedOn:DATE, pages:INT, totalWords: INT, chars:INT, apptype:LONGTEXT, security:INT, lines:INT, parag: INT, comp: LONGTEXT, charspace: INT, shared:LONGTEXT, appversion:FLOAT, fulltext:TEXT

import xml.etree.ElementTree as ET
import re
import zipfile
import sys
import string


def process(fullpath, config, rcontext, columns=None):
	try:
		document = zipfile.ZipFile(fullpath)
	# 	xmlfile = open("test.xml", "rw+")
	# 	xml = document.read("word/document.xml")
	# 	xmlfile.write(xml)
	# 	xmlfile.close()
	# 	print "OK"
	except:
		exit()


	# get content/text
	xml = document.read("word/document.xml")
	
	# document core, ie. keywords/title/subject and mod+creation dates
	xmlprop = document.read("docProps/core.xml")

	# data regarding ammount of pages/words. Also contains app version and OS.
	xmlapp = document.read("docProps/app.xml")

	# Finding content (Text)
	maincontent = re.compile('<w:t([^>]*)>([^<]*)</w:t>')
	tuples = maincontent.findall(xml)
	textcontent = ""

	# MSWord splits every word into seperate xml tags. 
	# Adding them to a single string instead
	for tuple in tuples:		
		textcontent = textcontent + "%s" % (tuple[1].rstrip('\n'))


# 	textcontent = textcontent.translate(None, '!.,\'\":;@#$')
# 	textsplit = textcontent.split(" ")
# 	print textsplit

	# Minidom alternative
	tree = ET.fromstring(xmlprop)
	tree_app = ET.fromstring(xmlapp)

	#### Just some data, might be usefull lat0r ####
	data_tree = []
	data_app = []
	merged = []

# 	for basic in range(9):
# 		data_tree.append(tree[basic].text)

# 	for app in range(16):
# 		data_app.append(tree_app[app].text)

	data_tree.append(tree[0].text)
	data_tree.append(tree[1].text)
	data_tree.append(tree[2].text)
	data_tree.append(tree[5].text)        
	data_tree.append(tree[6].text)
	data_tree.append(tree[7].text)
	data_tree.append(tree[8].text)
	data_app.append(tree_app[2].text)
	data_app.append(tree_app[3].text)
	data_app.append(tree_app[4].text)
	data_app.append(tree_app[5].text)
	data_app.append(tree_app[6].text)
	data_app.append(tree_app[7].text)
	data_app.append(tree_app[8].text)
	data_app.append(tree_app[10].text)
	data_app.append(tree_app[12].text)
	data_app.append(tree_app[12].text)
	data_app.append(tree_app[15].text)
	
# 	merged = data_tree + data_app
# 	merged.append(textcontent) 

	merged = data_tree + data_app
	merged.append(textcontent)
	return merged
	
# 	title = tree[0].text
# 	subject = tree[1].text
# 	author = tree[2].text
# 	changedBy = tree[5].text
# 	revision = tree[6].text
# 	createdOn = tree[7].text
# 	changedOn = tree[8].text
#
# 	pages = tree_app[2].text
# 	words = tree_app[3].text
# 	chars = tree_app[4].text
# 	apptype = tree_app[5].text
# 	security = tree_app[6].text
# 	lines = tree_app[7].text
# 	parag = tree_app[8].text
# 	comp = tree_app[10[.text
# 	charspace = tree_app[12].text
# 	shared = tree_app[12].text
# 	appversion = tree_app[15.text