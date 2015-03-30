#!/usr/bin/env python

# Copyright (C) 2013-2015 A. Eijkhoudt and others

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# TABLE: creation_date:TEXT, modified_date:TEXT, save_date:TEXT, author:TEXT, producer:TEXT, page_count:INT, content:LONGTEXT


import tika
import extract


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    parser = tika.AutoDetectParser()

    input = tika.FileInputStream(tika.File(fullpath))

    content = tika.BodyContentHandler()
    metadata = tika.Metadata()
    context = tika.ParseContext()
    
    parser.parse(input,content,metadata,context)
    content = content.toString()

    processed = [
        metadata.get("Creation-Date"),
        metadata.get("Last-Modified"),
        metadata.get("Last-Save-Date"),
        metadata.get("Author"),
        metadata.get("producer"),
        metadata.get("xmpTPg:NPages"),
        content
    ]

    extract.xpdf_extract(fullpath, config, rcontext)

    return processed
