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

# TABLE: author:LONGTEXT, changedBy:LONGTEXT, createdOn:LONGTEXT, changedOn:LONGTEXT, appType:LONGTEXT, security:INT, company:LONGTEXT, shared:LONGTEXT, appVersion:FLOAT, totalSheets:INT, content:LONGTEXT

import xml.etree.ElementTree as ET
import re
import zipfile
import sys
import os
import xlrd


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

    excelfile = xlrd.open_workbook(fullpath)
    numsheets = 0
    sheets = excelfile.sheet_names()

    sheetdata = []

    for sheet in sheets:
        numsheets += 1
        sheetname = excelfile.sheet_by_name(sheet)

        # Thanks to Joshua Burns for Cell calls tutorial
        num_rows = sheetname.nrows - 1
        num_cells = sheetname.ncols - 1
        curr_row = -1

        sheetdata.append({"Sheet": numsheets, "Content": []})

        while curr_row < num_rows:
            curr_row += 1
            row = sheetname.row(curr_row)
            curr_cell = -1
            celldata = []

            while curr_cell < num_cells:
                curr_cell += 1
                cell_type = sheetname.cell_type(curr_row, curr_cell)
                cell_value = sheetname.cell_value(curr_row, curr_cell)
                if not cell_type == 0 and not cell_type == 6:
                    coords = str(curr_row) + "." + str(curr_cell)
                    for val in sheetdata:
                        if val["Sheet"] == numsheets:
                            val["Content"].append({"Cell": coords, "Data": cell_value})

    merged = data_tree + data_app
    merged.append(work_total)
    merged.append(sheetdata)
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
