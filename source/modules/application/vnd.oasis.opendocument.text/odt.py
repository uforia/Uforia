#!/usr/bin/env python

#TABLE: wordCount:INT, imageCount:INT, objectCount:INT, pageCount:INT, charCount: INT, parCount: INT, tableCount: INT, content:TEXT 

import re, zipfile, sys
import BeautifulSoup


def process(fullpath, config, columns=None):
	try:
		document = zipfile.ZipFile(fullpath)
	except:
		exit()


	#get content/text
	xml = document.read("content.xml")

	#get metadata	
	xmlmeta = document.read("meta.xml")

	# Finding content (Text)
	maincontent = re.compile('<text:p([^>]*)>([^<]*)</text:p>')
	listtotal = maincontent.findall(xml)
	textcontent = ""
	
	#MSWord/odt splits every word into seperate xml tags. Adding them to a single string instead
	for words in listtotal:		
		textcontent = textcontent + "%s" % (words[1].rstrip('\n') )


	#Minidom alternative
	xmlsoup = BeautifulSoup.BeautifulSoup(xmlmeta)
	
	odtdict = ""
	for message in xmlsoup.findAll('meta:document-statistic'):
		odtdict = dict(message.attrs)
	
	results = []
	results.append(odtdict["meta:word-count"])
	results.append(odtdict["meta:image-count"])
	results.append(odtdict["meta:object-count"])
	results.append(odtdict["meta:page-count"])
	results.append(odtdict["meta:character-count"])
	results.append(odtdict["meta:paragraph-count"])
	results.append(odtdict["meta:table-count"])
	results.append(textcontent)

	return results
