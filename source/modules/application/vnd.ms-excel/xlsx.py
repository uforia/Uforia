#!/usr/bin/env python

# TABLE: author:LONGTEXT, changedBy:LONGTEXT, createdOn:LONGTEXT, changedOn:LONGTEXT, appType:LONGTEXT, security:INT, company:LONGTEXT, shared:LONGTEXT, appVersion:FLOAT, totalSheets:INT

import xml.etree.ElementTree as ET
import re
import zipfile
import sys
import os


def process(fullpath, config, rcontext, columns=None):
	try:
		document = zipfile.ZipFile(fullpath)
	except:
		exit()

	worksheets = []
	work_total = 0
	for x in document.namelist():
		if "/worksheets/" in x:
			worksheets.append(x)
			work_total += 1

# 	xml = document.read("xl/worksheets/sheet1.xml")
	
	# document core, ie. keywords/title/subject and mod+creation dates
	xmlprop = document.read("docProps/core.xml")

	# data regarding ammount of pages/words. Also contains app version and OS.
	xmlapp = document.read("docProps/app.xml")

	# Minidom alternative
	tree = ET.fromstring(xmlprop)
	tree_app = ET.fromstring(xmlapp)

	#### Just some data, might be usefull lat0r ####
	data_tree = []
	data_app = []

	for basic in range(4):
		data_tree.append(tree[basic].text)


# 	for app in range(10):
# 		data_app.append(tree_app[app].text)
	data_app.append(tree_app[0].text)
	data_app.append(tree_app[1].text)
	data_app.append(tree_app[5].text)
	data_app.append(tree_app[7].text)
	data_app.append(tree_app[9].text)

	merged = data_tree + data_app
	merged.append(work_total)
	return merged

# 	author = tree[0].text
# 	changedBy = tree[1].text
# 	createdOn = tree[2].text
# 	changedOn = tree[3].text

# 	apptype = tree_app[0].text
# 	security = tree_app[1].text
# 	company = tree_app[5].text
# 	shared = tree_app[7].text
# 	appversion = tree_app[9].text