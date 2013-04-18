#!/usr/bin/env python

#TABLE author:VARCHAR, changedBy:VARCHAR, createdOn:VARCHAR, changedOn:VARCHAR, appType:VARCHAR, security:INT, company:VARCHAR, shared:VARCHAR, appVersion:FLOAT, totalSheets:INT

import xml.etree.ElementTree as ET
import re, zipfile, sys, os

def process(fullpath, config, columns=None):
	try:
		document = zipfile.ZipFile(fullpath)
	except:
		exit()

	
	worksheets = []
	workTotal = 0
	for x in document.namelist():
		if "/worksheets/" in x:
			worksheets.append(x)
			workTotal += 1

#	xml = document.read("xl/worksheets/sheet1.xml")
	
	#document core, ie. keywords/title/subject and mod+creation dates
	xmlprop = document.read("docProps/core.xml")

	#data regarding ammount of pages/words. Also contains app version and OS.
	xmlapp = document.read("docProps/app.xml")

	#Minidom alternative
	tree = ET.fromstring(xmlprop)
	treeApp = ET.fromstring(xmlapp)

	#### Just some data, might be usefull lat0r ####
	dataTree = []
	dataApp = []

	for basic in range(4):
		dataTree.append(tree[basic].text)

	
#	for app in range(10):
#		dataApp.append(treeApp[app].text)
	dataApp.append(treeApp[0].text)
	dataApp.append(treeApp[1].text)
	dataApp.append(treeApp[5].text)
	dataApp.append(treeApp[7].text)
	dataApp.append(treeApp[9].text)


	merged = dataTree + dataApp
	merged.append(workTotal)
	return merged

#	author = tree[0].text
#	changedBy = tree[1].text
#	createdOn = tree[2].text
#	changedOn = tree[3].text

#	apptype = treeApp[0].text
#	security = treeApp[1].text
#	company = treeApp[5].text
#	shared = treeApp[7].text
#	appversion = treeApp[9].text

