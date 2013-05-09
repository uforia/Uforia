#!/usr/bin/env python

# TABLE: wordCount:INT, imageCount:INT, objectCount:INT, pageCount:INT, charCount: INT, parCount: INT, tableCount: INT, content:TEXT 

import re, zipfile, sys, bs4


def process(fullpath, config, rcontext, columns=None):
    try:
    	document = zipfile.ZipFile(fullpath)
    except:
    	exit()


    # get content/text
    xml = document.read("content.xml")

    # get metadata	
    xmlmeta = document.read("meta.xml")

    # Finding content (Text)
    maincontent = re.compile('<text:p([^>]*)>([^<]*)</text:p>')
    listtotal = maincontent.findall(xml)
    textcontent = ""
    
    # MSWord/odt splits every word into seperate xml tags. Adding them to a single string instead
    for words in listtotal:		
    	textcontent = textcontent + "%s" % (words[1].rstrip('\n'))


    # Minidom alternative
    xmlsoup = bs4.BeautifulSoup(xmlmeta)
    
    odtdict = ""
    for message in xmlsoup.findAll('meta:document-statistic'):
    	odtdict = dict(message.attrs)

    results = []
    for i in ('meta:word-count', 'meta:image-count', 'meta:row-count', 'meta:character-count', 'meta:non-whitespace-character-count', 'meta:paragraph-count', 'meta-page-count'):
        try:
            results.append(odtdict[i])
        except KeyError:
            results.append('')
    results.append(textcontent)
    return results
