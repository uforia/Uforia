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
# TABLE: Date:DATETIME,Content:LONGTEXT,Create:DATE,Modify:DATE,Access:DATE,Update:DATE,Delete:DATE,Internal_Create:DATE,Name:LONGTEXT,Description:LONGTEXT,Extension:LONGTEXT,Type:LONGTEXT,Status:LONGTEXT,Type_Description:LONGTEXT,Category:LONGTEXT,Evidence_Object:LONGTEXT,Path:LONGTEXT,Sender:LONGTEXT,Recipients:LONGTEXT,Size:LONGTEXT,CreateTimestamp:DATETIME,ModifyTimestamp:DATETIME,AccessTimestamp:DATETIME,UpdateTimestamp:DATETIME,DeleteTimestamp:DATETIME,Internal_CreateTimestamp:DATETIME,Attributes:LONGTEXT,Owner:LONGTEXT,Links:BIGINT,File_Count:BIGINT,Sector:BIGINT,ID:BIGINT,Internal_ID:BIGINT,Internal_Parent:BIGINT,Dimension:LONGTEXT,SCPercent:LONGTEXT,Hash:LONGTEXT,Hash_Set:LONGTEXT,Hash_Category:LONGTEXT,Report_Table:LONGTEXT,Comment:LONGTEXT,Metadata:LONGTEXT

import os,sys,traceback,shutil,recursive,datetime,time,tempfile

def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath
        f = open(fullpath,'r')
        if "/nontampered_" not in fullpath:
            return None
        if "Name;Description;Ext.;Type;Status;Type descr.;Category;Evidence object;Path;Sender;Recipients;Size;Created;Modified;Accessed;Record update;Deletion;Int. creation;Attr.;Owner;Links;File count;1st sector;ID;Int. ID;Int. parent;Dimens.;SC%;Hash;Hash Set;Hash Categ.;Report table;Comment;Metadata" not in f.read():
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
                    secondline = f.readline().strip()
                    itemlist = secondline.split(';')

                    Name                    = itemlist[0]
                    Description             = itemlist[1] if itemlist[1] else None
                    Extension               = itemlist[2] if itemlist[2] else None
                    Type                    = itemlist[3] if itemlist[3] else None
                    Status                  = itemlist[4] if itemlist[4] else None
                    Type_Description        = itemlist[5] if itemlist[5] else None
                    Category                = itemlist[6] if itemlist[6] else None
                    Evidence_Object         = itemlist[7] if itemlist[7] else None
                    Path                    = itemlist[8] if itemlist[8] else None
                    Sender                  = itemlist[9] if itemlist[9] else None
                    Recipients              = itemlist[10] if itemlist[10] else None
                    Size                    = itemlist[11] if itemlist[11] else None
                    
                    RawDate	                = itemlist[12].split(' ')[0]
                    try:
                        Day,Month,Year          = RawDate.split('-')
                        Date                    = '{:02}'.format(int(Day))+'-'+'{:02}'.format(int(Month))+'-'+'{:04}'.format(int(Year))
                        Time    	         	= itemlist[12].split(' ')[1]
                        Time += ":00" if len(Time) < 6 else Time
                        Created     	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d-%m-%Y %H:%M:%S'))).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        Created                 = "1970-01-01 00:00:00"

                    RawDate	                = itemlist[13].split(' ')[0]
                    try:
                        Day,Month,Year          = RawDate.split('-')
                        Date                    = '{:02}'.format(int(Day))+'-'+'{:02}'.format(int(Month))+'-'+'{:04}'.format(int(Year))
                        Time    	         	= itemlist[13].split(' ')[1]
                        Time += ":00" if len(Time) < 6 else Time
                        Modified     	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d-%m-%Y %H:%M:%S'))).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        Modified                = "1970-01-01 00:00:00"

                    RawDate 	                = itemlist[14].split(' ')[0]
                    try:
                        Day,Month,Year          = RawDate.split('-')
                        Date                    = '{:02}'.format(int(Day))+'-'+'{:02}'.format(int(Month))+'-'+'{:04}'.format(int(Year))
                        Time    	         	= itemlist[14].split(' ')[1]
                        Time += ":00" if len(Time) < 6 else Time
                        Accessed     	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d-%m-%Y %H:%M:%S'))).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        Accessed                = "1970-01-01 00:00:00"

                    RawDate	                    = itemlist[15].split(' ')[0]
                    try:
                        Day,Month,Year          = RawDate.split('-')
                        Date                    = '{:02}'.format(int(Day))+'-'+'{:02}'.format(int(Month))+'-'+'{:04}'.format(int(Year))
                        Time    	         	= itemlist[15].split(' ')[1]
                        Time += ":00" if len(Time) < 6 else Time
                        Updated     	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d-%m-%Y %H:%M:%S'))).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        Updated                 = "1970-01-01 00:00:00"

                    RawDate	                    = itemlist[16].split(' ')[0]
                    try:
                        Day,Month,Year          = RawDate.split('-')
                        Date                    = '{:02}'.format(int(Day))+'-'+'{:02}'.format(int(Month))+'-'+'{:04}'.format(int(Year))
                        Time    	         	= itemlist[16].split(' ')[1]
                        Time += ":00" if len(Time) < 6 else Time
                        Deleted     	        = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d-%m-%Y %H:%M:%S'))).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        Deleted                 = "1970-01-01 00:00:00"

                    RawDate	                    = itemlist[17].split(' ')[0]
                    try:
                        Day,Month,Year          = RawDate.split('-')
                        Date                    = '{:02}'.format(int(Day))+'-'+'{:02}'.format(int(Month))+'-'+'{:04}'.format(int(Year))
                        Time    	         	= itemlist[17].split(' ')[1]
                        Time += ":00" if len(Time) < 6 else Time
                        Internally_Created      = datetime.datetime.fromtimestamp(time.mktime(time.strptime(Date+' '+Time,'%d-%m-%Y %H:%M:%S'))).strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        Internally_Created      = "1970-01-01 00:00:00"

                    Attributes              = itemlist[18].strip() if itemlist[18] else None
                    Owner                   = itemlist[19].strip() if itemlist[19] else None
                    Links                   = itemlist[20].strip() if itemlist[20] else None
                    File_Count              = itemlist[21].strip() if itemlist[21] else None
                    Sector                  = itemlist[22].strip() if itemlist[22] else None
                    ID                      = itemlist[23].strip() if itemlist[23] else None
                    Internal_ID             = itemlist[24].strip() if itemlist[24] else None
                    Internal_Parent         = itemlist[25].strip() if itemlist[25] else None
                    Dimension               = itemlist[26].strip() if itemlist[26] else None
                    SCPercent               = itemlist[27].strip() if itemlist[27] else None
                    Hash                    = itemlist[28].strip() if itemlist[28] else None
                    Hash_Set                = itemlist[29].strip() if itemlist[29] else None
                    Hash_Category           = itemlist[30].strip() if itemlist[30] else None
                    Report_Table            = itemlist[31].strip() if itemlist[31] else None
                    Comment                 = itemlist[32].strip() if itemlist[32] else None
                    Metadata                = itemlist[33].strip() if itemlist[33] else None

                    C,M,A,U,D,I             = Created.split(' ')[0],Modified.split(' ')[0],Accessed.split(' ')[0],Updated.split(' ')[0],Deleted.split(' ')[0],Internally_Created.split(' ')[0]

                    detail                  =  "<table><tr>"
                    detail                  += "<th>File</th><td>"+Path+"\\"+Name+"</td>"
                    detail                  += "</tr><tr>"
                    detail                  += "<th>Size</th><td>"+str(Size)+"</td>"
                    detail                  += "</tr><tr>"
                    detail                  += "<th>Created</th><td>"+Created+"</td>"
                    detail                  += "</tr><tr>"
                    detail                  += "<th>Modified</th><td>"+Modified+"</td>"
                    detail                  += "</tr><tr>"
                    detail                  += "<th>Accessed</th><td>"+Accessed+"</td>"
                    detail                  += "</tr><tr>"
                    detail                  += "<th>Updated</th><td>"+Updated+"</td>"
                    detail                  += "</tr><tr>"
                    detail                  += "<th>Deleted</th><td>"+Deleted+"</td>"
                    detail                  += "</tr></table>"

                    Row=[Created,detail,C,M,A,U,D,I,Name,Description,Extension,Type,Status,Type_Description,Category,Evidence_Object,Path,Sender,Recipients,Size,Created,Modified,Accessed,Updated,Deleted,Internally_Created,Attributes,Owner,Links,File_Count,Sector,ID,Internal_ID,Internal_Parent,Dimension,SCPercent,Hash,Hash_Set,Hash_Category,Report_Table,Comment,Metadata]
                
                    if config.DEBUG:
                        print "\nTimeline data:"
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
#                try:
#                    shutil.rmtree(tmpdir)
#                except:
#                    traceback.print_exc(file=sys.stderr)
                return None
