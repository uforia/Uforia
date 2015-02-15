#!/usr/bin/env python

# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# TABLE: word_count:INT, image_count:INT, object_count:INT, page_count:INT, character_count: INT, paragraph_count: INT, table_count: INT, content:TEXT

import re
import zipfile
import sys
import bs4


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
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

    # MSWord/odt splits every word into seperate xml tags.
    # Adding them to a single string instead
    for words in listtotal:
        textcontent = textcontent + "%s" % (words[1].rstrip('\n'))


    # Minidom alternative
    xmlsoup = bs4.BeautifulSoup(xmlmeta)

    odtdict = ""
    for message in xmlsoup.findAll('meta:document-statistic'):
        odtdict = dict(message.attrs)

    results = []
    for i in ('meta:word-count', 'meta:image-count', 'meta:row-count',
    'meta:character-count', 'meta:non-whitespace-character-count',
    'meta:paragraph-count', 'meta-page-count'):
        try:
            results.append(odtdict[i])
        except KeyError:
            results.append('')
    results.append(textcontent)
    return results
