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

# TABLE: created:LONGTEXT, adjustedDate:LONGTEXT, adjustedCount:INT, content:LONGTEXT

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
    mainpage = re.compile('<table:table table:name=(.*?)table:style-name="ta1">(.*?)</table:table>')
    maintotal = mainpage.findall(xml)
    pages = []
    pageno = 0

    for test in maintotal:
        rownu = 0
        colnu = 0
        test = ''.join(test[1])
        maincontent = re.compile('<table:table-row table:style-name="ro1">(.*?)</table:table-row>')
        contenttotal = maincontent.findall(test)
        for rows in contenttotal:
            rownu += 1
            textcontent = re.compile('<text:p>(.*?)</text:p>')
            textfind = textcontent.findall(rows)
        for cols in textfind:
            colnu += 1
            cellnu = str(1) + "." + str(colnu)
            pages.append({"Cell": cellnu, "Content": cols})

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
