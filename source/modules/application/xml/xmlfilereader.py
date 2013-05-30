# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# This is the module for .XML

# TABLE: version:DOUBLE, encoding:LONGTEXT, standalone:LONGTEXT, content:LONGTEXT

import sys
import traceback


def process(fullpath, config, rcontext, columns=None):
        # Try to parse XML data
        try:
            assorted = []

            # Open the XML file
            xml = open(fullpath, 'r')

            # Get header of XML file
            for line in xml:
                if line.startswith("<?xml"):
                    header = line.split("?>")[0]

                    # Get version from header
                    version_index = header.find("version=\"")
                    if version_index != -1:
                        # Add 9 because we want to start after version="
                        version_index += 9
                        version = header[version_index:
                                         header.find("\"", version_index)]
                        assorted.append(float(version))
                    else:
                        assorted.append(None)

                    # Get Encoding form header
                    encoding_index = header.find("encoding=\"")
                    if encoding_index != -1:
                        # Add 10 because we want to start after encoding="
                        encoding_index += 10
                        encoding = header[encoding_index:
                                          header.find("\"", encoding_index)]
                        assorted.append(encoding)
                    else:
                        assorted.append(None)

                    # Get Encoding form header
                    standalone_index = header.find("standalone=\"")
                    if standalone_index != -1:
                        # Add 12 because we want to start after standalone="
                        standalone_index += 12
                        standalone = header[standalone_index:
                                            header.find("\"",
                                                        standalone_index)]
                        assorted.append(standalone)
                    else:
                        assorted.append(None)

                    # Break for loop
                    break

            if len(assorted) == 0:
                raise Exception("XML header not found, All XML files should" +
                                "have an header.")

            # Start reading from top
            xml.seek(0)
            # Add whole xml file to database
            assorted.append(xml.read())

            # Make sure we stored exactly the same amount of columns as
            # specified!!
            assert len(assorted) == len(columns)

            # Print some data that is stored in the database if debug is true
            if config.DEBUG:
                print "\nXML file data:"
                for i in range(0, len(assorted)):
                    print "%-18s %s" % (columns[i] + ':', assorted[i])

            return assorted

        except:
            traceback.print_exc(file=sys.stderr)

            # Store values in database so not the whole application crashes
            return None
