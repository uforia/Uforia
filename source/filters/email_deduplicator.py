#!/usr/bin/env python

# Copyright (C) 2013-2015 A. Eijkhoudt and others

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

from hashlib import sha256

FILTERED_HEADERS = ["Message-ID:", "X-Folder:"]

def process(file_paths):
    """
    Checks if the file is unique. Because Outlook adds two headers,
    we strip those to make before we check if the file is unique.
    """
    return_paths = dict()
    for path, n in file_paths:
        email_array = []
        with open(path, 'r') as infile:

            # Read the contents of the file into an array.
            # Skip the line if it contains the headers
            for line in infile:
                if not header_contains(line):
                    email_array.append(line)

            # Convert the array to a string, then calculate the sha256 digest.
            text = ''.join([str(line) for line in email_array]).encode()

            return_paths[sha256(text).hexdigest()] = path

    for element in file_paths:
        if element[0] not in return_paths.values():
            file_paths.remove(element)

    return file_paths


def header_contains(line):
    """
    Returns True if the line contains headers present in
    DECLUDED_HEADERS.
    """
    for header in FILTERED_HEADERS:
        if line.startswith(header):
            return True

if __name__ == '__main__':
    testFilePaths = [
            "/home/dervos/code/Uforia/TESTDATA/email1 (another copy).eml",
            "/home/dervos/code/Uforia/TESTDATA/email1 (copy).eml",
            "/home/dervos/code/Uforia/TESTDATA/email1.eml"
            ]
    outputPaths = process(testFilePaths)
    print("Test Filepaths: ")
    print(testFilePaths)
    print("Output after deduplicator Filepaths: ")
    print(outputPaths)
