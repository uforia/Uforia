#!/usr/bin/env python

#TABLE: title:LONGTEXT, subject:LONGTEXT, author:LONGTEXT, changedBy:LONGTEXT, revision:INT, createdOn:DATE, changedOn:DATE, pages:INT, totalWords: INT, chars:INT, apptype:LONGTEXT, security:INT, lines:INT, parag: INT, comp: LONGTEXT, charspace: INT, shared:LONGTEXT, appversion:FLOAT, fulltext:TEXT

import xml.etree.ElementTree as ET
import re,zipfile,sys,string

def process(fullpath, config, columns=None):
	try:
		document = zipfile.ZipFile(fullpath)
	#	xmlfile = open("test.xml", "rw+")
	#	xml = document.read("word/document.xml")
	#	xmlfile.write(xml)
	#	xmlfile.close()
	#	print "OK"
	except:
		exit()


	#get content/text
	xml = document.read("word/document.xml")
	
	#document core, ie. keywords/title/subject and mod+creation dates
	xmlprop = document.read("docProps/core.xml")

	#data regarding ammount of pages/words. Also contains app version and OS.
	xmlapp = document.read("docProps/app.xml")

	# Finding content (Text)
	maincontent = re.compile('<w:t([^>]*)>([^<]*)</w:t>')
	tuples = maincontent.findall(xml)
	textcontent = ""
	
	#MSWord splits every word into seperate xml tags. Adding them to a single string instead
	for tuple in tuples:		
		textcontent = textcontent + "%s" % (tuple[1].rstrip('\n') )


#	textcontent = textcontent.translate(None, '!.,\'\":;@#$')
#	textsplit = textcontent.split(" ")
#	print textsplit

	#Minidom alternative
	tree = ET.fromstring(xmlprop)
	treeApp = ET.fromstring(xmlapp)

	#### Just some data, might be usefull lat0r ####
	dataTree = []
	dataApp = []
	merged = []
#	for basic in range(9):
#		dataTree.append(tree[basic].text)
	
#	for app in range(16):
#		dataApp.append(treeApp[app].text)

#	merged = dataTree + dataApp
#	merged.append(textcontent) 


        dataTree.append(tree[0].text)
        dataTree.append(tree[1].text)
        dataTree.append(tree[2].text)
        dataTree.append(tree[5].text)        
        dataTree.append(tree[6].text)
        dataTree.append(tree[7].text)
        dataTree.append(tree[8].text)
#
        dataApp.append(treeApp[2].text)
        dataApp.append(treeApp[3].text)
        dataApp.append(treeApp[4].text)
        dataApp.append(treeApp[5].text)
        dataApp.append(treeApp[6].text)
        dataApp.append(treeApp[7].text)
        dataApp.append(treeApp[8].text)
        dataApp.append(treeApp[10].text)
        dataApp.append(treeApp[12].text)
        dataApp.append(treeApp[12].text)
        dataApp.append(treeApp[15].text)

	merged = dataTree + dataApp
	merged.append(textcontent)
	return merged
	
#	title = tree[0].text
#	subject = tree[1].text
#	author = tree[2].text
#	changedBy = tree[5].text
#	revision = tree[6].text
#	createdOn = tree[7].text
#	changedOn = tree[8].text
#
#	pages = treeApp[2].text
#	words = treeApp[3].text
#	chars = treeApp[4].text
#	apptype = treeApp[5].text
#	security = treeApp[6].text
#	lines = treeApp[7].text
#	parag = treeApp[8].text
#	comp = treeApp[10[.text
#	charspace = treeApp[12].text
#	shared = treeApp[12].text
#	appversion = treeApp[15.text






