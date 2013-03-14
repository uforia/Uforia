#!/usr/bin/env python
import os, sys

os.environ['LD_LIBRARY_PATH'] = './libraries/libxmp/bin/'
sys.path.insert(0, "./libries/libxmp/bin/")

os.system(sys.executable + ' Uforia.py')
