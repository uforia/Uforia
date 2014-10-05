# Copyright (C) 2013 Hogeschool van Amsterdam

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
# TABLE: Delivered_To:LONGTEXT, Original_Recipient:LONGTEXT, Received:LONGTEXT, Return_Path:LONGTEXT, Received_SPF:LONGTEXT, Authentication_Results:LONGTEXT, DKIM_Signature:LONGTEXT, DomainKey_Signature:LONGTEXT, Organization:LONGTEXT, MIME_Version:DOUBLE, List_Unsubscribe:LONGTEXT, X_Received:LONGTEXT, X_Priority:LONGTEXT, X_MSMail_Priority:LONGTEXT, X_Mailer:LONGTEXT, X_MimeOLE:LONGTEXT, X_Notifications:LONGTEXT, X_Notification_ID:LONGTEXT, X_Sender_ID:LONGTEXT, X_Notification_Category:LONGTEXT, X_Notification_Type:LONGTEXT, X_UB:INT, Precedence:LONGTEXT, Reply_To:LONGTEXT, Auto_Submitted:LONGTEXT, Message_ID:LONGTEXT, Date:DATE, Subject:LONGTEXT, From:LONGTEXT, To:LONGTEXT, Content_Type:LONGTEXT, XTo:LONGTEXT, Xcc:LONGTEXT, Xbcc:LONGTEXT, Cc:LONGTEXT, Bcc:LONGTEXT, Email_Content:LONGTEXT

import sys
import traceback
from email.parser import Parser
import python_dateutil.dateutil.parser as date_parser
import re

def process(file, config, rcontext, columns=None):
        fullpath = file.fullpath

        # Try to parse rfc822 data
        try:
            #  Get the e-mail headers from a file
            email = open(fullpath, 'r')
            headers = Parser().parse(email)

            # Get most common headers
            try:
                ReplyTo = re.sub(r'\s+',' ',headers["Reply-To"]).lstrip()
            except:
                ReplyTo = None
            try:
                To = re.sub(r'\s+',' ',headers["To"]).lstrip()
            except:
                To = None
            try:
                From = re.sub(r'\s+',' ',headers["From"]).lstrip()
            except:
                From = None
            try:
                XTo = re.sub(r'\s+',' ',headers["X-To"]).lstrip()
            except:
                XTo = None
            try:
                Xcc = re.sub(r'\s+',' ',headers["X-Cc"]).lstrip()
            except:
                Xcc = None
            try:
                Xbcc = re.sub(r'\s+',' ',headers["X-Bcc"]).lstrip()
            except:
                Xbcc = None
            try:
                Cc = re.sub(r'\s+',' ',headers["Cc"]).lstrip()
            except:
                Cc = None
            try:
                Bcc = re.sub(r'\s+',' ',headers["Bcc"]).lstrip()
            except:
                Bcc = None
            assorted = [headers["Delivered-To"], headers["Original-Recipient"],
                        headers["Received"], headers["Return-Path"],
                        headers["Received-SPF"],
                        headers["Authentication-Results"],
                        headers["DKIM-Signature"],
                        headers["DomainKey-Signature"],
                        headers["Organization"], headers["MIME-Version"],
                        headers["List-Unsubscribe"], headers["X-Received"],
                        headers["X-Priority"], headers["X-MSMail-Priority"],
                        headers["X-Mailer"], headers["X-MimeOLE"],
                        headers["X-Notifications"],
                        headers["X-Notification-ID"],
                        headers["X-Sender-ID"],
                        headers["X-Notification-Category"],
                        headers["X-Notification-Type"], headers["X-UB"],
                        headers["Precedence"], ReplyTo,
                        headers["Auto-Submitted"], headers["Message-ID"],
                        date_parser.parse(headers["Date"]),
                        headers["Subject"], From, To, headers["Content-Type"],
                        XTo, Xcc, Xbcc, Cc, Bcc]

            # Start at the beginning of the file
            email.seek(0)

            # Put whole email file in database
            assorted.append(email.read())

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nrfc822 file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i] + ':', assorted[i])

            return assorted
        except TypeError:
            print('TypeError')
            pass
        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
