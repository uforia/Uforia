# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


#!/usr/bin/env python

# TABLE: created:LONGTEXT, modified_date:LONGTEXT, modified_count:INT, content:LONGTEXT

import re
import zipfile
import sys


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
    mainpage = re.compile('<draw:page(.*?)</draw:page>')
    maintotal = mainpage.findall(xml)
    pages = []
    pageno = 0

    for test in maintotal:
        pageno += 1
        test = ''.join(test)
        maincontent = re.compile('<text:p([^>]*)>([^<]*)(</text:p>|<text:tab/>)')
        contenttotal = maincontent.findall(test)
        textcontent = ""
        for words in contenttotal:
            textcontent = textcontent + "%s " % (words[1].rstrip('\n'))
        pages.append({"Sheet": pageno, "Content": textcontent})

    odtdict = []
    results = []

    for i in ('<meta:creation-date>(.*?)</', '<dc:date>(.*?)</',
    '<meta:editing-cycles>(.*?)</'):
        try:
            metainfo = re.compile(i)
            contentmeta = metainfo.findall(xmlmeta)
            results.append(contentmeta)
        except KeyError:
            results.append('')
    results.append(pages)

    return results
