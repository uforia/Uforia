# Copyright (C) 2013 Hogeschool van Amsterdam

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# Implement generic extraction/recursion support for multiple modules.
import subprocess
import tika
import recursive
import tempfile
import os
import sys
import shutil
import traceback


def _do_tika_extract(fullpath, tempdir):
    # Path that leads to the archive
    if fullpath is None:
        raise Exception("Archive path not given")

    # Path that leads to the destination
    if tempdir is None:
        raise Exception("Tempdir not given")

    # Set tika location
    tika_jar_path = os.path.abspath("./libraries/tika/tika-app-1.3.jar")
    if not os.path.exists(tika_jar_path):
        raise Exception("Tika not found at " + tika_jar_path)

    p = subprocess.Popen(["java",
                          "-jar",
                          tika_jar_path,
                          "--extract",
                          fullpath],
                         cwd=tempdir)
    output = p.communicate()[0]

    if output is not None:
        raise Exception("tika extract command failed")


def tika_extract(fullpath, context, metadata, config, rcontext):
    """
    Use the Tika input stream and extract all embedded files (if possible). Invokes Uforia
    recursively over the extracted files.
    fullpath - Path of the file to extract
    context - The Tika parse context
    metadat - Tika metadata object
    oonfig - The Uforia configuration file
    rcontext - The Uforia recursion context variables
    """
    # To skip recursive call if there are no files to extract
    extractor = tika.ParsingEmbeddedDocumentExtractor(context)
    needs_extraction = extractor.shouldParseEmbedded(metadata)

    if needs_extraction:
        # Call Uforia recursively on embedded files
        tempdir = None
        try:
            # Perform extraction
            tempdir = tempfile.mkdtemp(dir=config.EXTRACTDIR)
            _do_tika_extract(fullpath, tempdir)

            # Call Uforia again
            recursive.call_uforia_recursive(config, rcontext, tempdir, fullpath)
        except:
            traceback.print_exc(file=sys.stderr)
        finally:
            try:
                if tempdir:
                    shutil.rmtree(tempdir)  # delete directory
            except OSError as exc:
                traceback.print_exc(file=sys.stderr)
