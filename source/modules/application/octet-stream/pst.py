# TABLE: file_names:LONGTEXT, total_files:INT, zip_stored:INT, zip_deflated:INT, debug:LONGTEXT, comment:LONGTEXT, content_info:LONGTEXT

import shutil
import subprocess
import sys
import tempfile
import traceback

import libutil
import recursive


def process(file, config, rcontext, columns=None):
    fullpath = file.fullpath
    if file.btype.startswith("Microsoft Outlook email folder"):
        readpst_path = libutil.get_executable("libpst", "readpst")

        tempdir = None

        try:
            tempdir = tempfile.mkdtemp(dir=config.EXTRACTDIR)

            p = subprocess.Popen([
                readpst_path,
                '-e',
                '-q',
                '-o',
                tempdir,
                fullpath
            ])

            err = p.communicate()[1]

            if err is not None:
                raise Exception("readpst failed to extract " + fullpath)

            recursive.call_uforia_recursive(config, rcontext, tempdir, fullpath)
        except:
            traceback.print_exc(file=sys.stderr)
        finally:
            try:
                if tempdir:
                    shutil.rmtree(tempdir)  # delete directory
            except OSError as exc:
                traceback.print_exc(file=sys.stderr)