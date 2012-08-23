#!/usr/bin/env python
import os
import sys

#If the executed file is the main file, the main file will use the settings from Django, imported from the following location:
if __name__ == "__main__":
	 os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Uforia.settings.settings")
	 from django.core.management import execute_from_command_line
	 execute_from_command_line(sys.argv)
