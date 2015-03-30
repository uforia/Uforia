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

# This is the module for handling rfc822 email types

# Do not change from CamelCase because these are the official header names
# TABLE: Date:DATETIME, From:LONGTEXT, To:LONGTEXT, Direction:LONGTEXT, Duration:LONGTEXT, ServiceCode:LONGTEXT, IMEI:LONGTEXT, CellID:LONGTEXT, SiteName:LONGTEXT, Suburb:LONGTEXT

import os,sys,traceback,shutil,recursive,datetime,time

def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath
        if "Date;Time;Called;Calling;Direction;Duration;ServiceCode;IMEI;CellID;SiteName;Suburb" not in open(fullpath,'r').read():
            return None

        # Try to parse the cell phone log
        try:
            #  Get first line from the file and check if it's in the cell log format
            assorted = []
            cell_file = open(fullpath, 'r')
            firstline = cell_file.readline().strip()
            # We have a match, start building the call log list, line by line, because we need to reconstruct timestamps
            for line in cell_file:
                itemlist = line.split(';')
                Date	                = itemlist[0]
                RawTime    	         	= str(itemlist[1])
                Time                    = RawTime.zfill(6)
                DateTime    	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d/%m/%y %H%M%S'))).strftime('%Y-%m-%d %H:%M:%S')
                From 	         	    = itemlist[2].strip() if itemlist[2] else None
                To   		        	= itemlist[3].strip() if itemlist[3] else None
                Direction             	= itemlist[4].strip() if itemlist[4] else None
                Duration            	= itemlist[5].strip() if itemlist[5] else '0'
                ServiceCode             = itemlist[6].strip() if itemlist[6] else 'No Code'
                IMEI     		        = itemlist[7].strip() if itemlist[7] else 'No IMEI'
                CellID          		= itemlist[8].strip() if itemlist[8] else 'Unknown'
                SiteName            	= itemlist[9].strip() if itemlist[9] else 'Unknown'
                Suburb   	        	= itemlist[10].strip() if itemlist[10] else 'Unknown'

                Row=[DateTime,From,To,Direction,Duration,ServiceCode,IMEI,CellID,SiteName,Suburb]
                assorted.append(Row)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\ncell phone data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i] + ':', assorted[i])

            #assert len(assorted) == len(columns)
            return assorted
        except TypeError:
            print('TypeError')
            pass
        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
