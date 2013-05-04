#!/usr/bin/env python

# TABLE: title:LONGTEXT, createdBy:LONGTEXT, modBy:LONGTEXT, revision:INT, madeOn:LONGTEXT, changedOn:LONGTEXT, totalLength: FLOAT, totalWords:INT, application:LONGTEXT, ppFormat:LONGTEXT, paragraphs:INT, slides:INT, notes:INT, hiddenSlides:INT, videos:INT, company:LONGTEXT, shared:LONGTEXT, version:FLOAT 

import xml.etree.ElementTree as ET
import re, zipfile, sys

def process(fullpath, config, columns=None):
	try:
		document = zipfile.ZipFile(fullpath)
	except:
		exit()

	# document core, ie. keywords/title/subject and mod+creation dates
	xmlprop = document.read("docProps/core.xml")

	# data regarding ammount of pages/words. Also contains app version and OS.
	xmlapp = document.read("docProps/app.xml")

	# Minidom alternative
	tree = ET.fromstring(xmlprop)
	treeApp = ET.fromstring(xmlapp)

	#### Just some data, might be usefull lat0r ####
	dataTree = []
	dataApp = []

# 	for basic in range(6):
# 		dataTree.append(tree[basic].text)
	
# 	for app in range(17):
# 		dataApp.append(treeApp[app].text)


	dataTree.append(tree[0].text)
	dataTree.append(tree[1].text)
	dataTree.append(tree[2].text)
	dataTree.append(tree[3].text)
	dataTree.append(tree[4].text)
	dataTree.append(tree[5].text)

	dataApp.append(treeApp[0].text)
	dataApp.append(treeApp[1].text)
	dataApp.append(treeApp[2].text)
	dataApp.append(treeApp[3].text)
	dataApp.append(treeApp[4].text)
	dataApp.append(treeApp[5].text)
	dataApp.append(treeApp[6].text)
	dataApp.append(treeApp[7].text)
	dataApp.append(treeApp[8].text)
	dataApp.append(treeApp[12].text)
	dataApp.append(treeApp[14].text)
	dataApp.append(treeApp[16].text)

	merged = dataTree + dataApp
	return merged

# 	title = tree[0].text
# 	created = tree[1].text
# 	lastmod = tree[2].text
# 	revision = tree[3].text
# 	madeon = tree[4].text
# 	changedon = tree[5].text

# 	time = treeApp[0].text
# 	words = treeApp[1].text
# 	application = treeApp[2].text
# 	ppFormat = treeApp[3].text
# 	paragraphs = treeApp[4].text
# 	slides = treeApp[5].text
# 	notes = treeApp[6].text
# 	hiddenslides = treeApp[7].text
# 	multimediaclips = treeApp[8].text
# 	company = treeApp[12].text
# 	shared = treeApp[14].text
# 	version = treeApp[16].text



