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

# TABLE: revNum:INT, lastPrint:TEXT, creatDate:TEXT, orAuth:TEXT, lastSaved:TEXT, content:LONGTEXT

import tika
def process(fullpath, config, rcontext, columns=None):

	results = []
	meta = []

	tika.initVM()

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
	allowedMeta = [0, 1, 4, 5, 7]

	for x in meta:
		if val in allowedMeta:
			results.append(x)
		val += 1
	
	results.append(content)

	return results
