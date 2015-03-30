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

# TABLE: pages:INT, creation_date:TEXT, author:TEXT, framework:TEXT, tool:TEXT, content:LONGTEXT

import tika
import extract

def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    results = []
    meta = []

    parser = tika.AutoDetectParser()

    input = tika.FileInputStream(tika.File(fullpath))

    content = tika.BodyContentHandler()
    metadata = tika.Metadata()
    context = tika.ParseContext()

    parser.parse(input,content,metadata,context)
    content = content.toString()

    for n in metadata.names():
        meta.append(metadata.get(n))

    val = 0
    parse = [0,3,4,7,9]

    for x in meta:
        if val in parse:
            results.append(x)
        val += 1

    results.append(content)

    extract.tika_extract(fullpath, context, metadata, config, rcontext);

    return results


