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

import os,sys,traceback,shutil,recursive,datetime,time,tempfile

def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath
        f = open(fullpath,'r')
        if "Date;Time;Called;Calling;Direction;Duration;ServiceCode;IMEI;CellID;SiteName;Suburb" not in f.read():
            return None
        else:
            f.seek(0)
            numlines = sum(1 for _ in f)
            if numlines < 1:
                # Empty file
                return None

            if numlines == 2:
                # Header and single line, should go into the database
                try:
                    f.seek(0)
                    firstline = f.readline().strip()
                    itemlist = f.readline().split(';')

                    Date	                = itemlist[0]
                    RawTime    	         	= str(itemlist[1])
                    Time                    = RawTime.zfill(6)
                    DateTime    	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d/%m/%Y %H%M%S'))).strftime('%Y-%m-%d %H:%M:%S')
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
                
                    if config.DEBUG:
                        print "\ncell phone data:"
                        for i in range(0, len(assorted)):
                            print "%-18s %s" % (columns[i] + ':', assorted[i])

                    return Row
                except TypeError:
                    print('TypeError')
                    pass
                except:
                    traceback.print_exc(file=sys.stderr)
                    return None              

            if numlines > 2:
                # Header and multiple lines, split up into files
                f.seek(0)
                firstline = f.readline().strip()
                secondline = f.readline()
                lineno = 1
                tmpdir = tempfile.mkdtemp("_uforiatmp", dir=config.EXTRACTDIR)
                targetdir = tmpdir + os.path.sep + os.path.dirname(fullpath)
                if not os.path.exists(targetdir):
                    try:
                        os.makedirs(targetdir)
                    except OSError as exc:
                        if exc.errno != errno.EXIST:
                            raise
                for line in f:
                    targetfile = fullpath + "_line_" + str(lineno).zfill(len(str(numlines)))
                    lineno += 1
                    with open(tmpdir+targetfile,'wb') as g:
                        g.write(firstline+'\n')
                        g.write(line)
                recursive.call_uforia_recursive(config,rcontext,tmpdir,os.path.dirname(fullpath))
                try:
                    shutil.rmtree(tmpdir)
                except:
                    traceback.print_exc(file=sys.stderr)
                return None
