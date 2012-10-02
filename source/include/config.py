#!/usr/bin/env python

# Enable debug output. Prints lots of information about internal workings.
# Note: Debug output is very noisy and should not be used in production.
DEBUG = True

# From which directory should Uforia start to scan?
# Example: STARTDIR = '/home/user/' 
STARTDIR = '/home/FILES/'

# Where should Uforia find the modules to handle found MIME types?
# Note: You should not normally have to modify this!
# Example: MODULES = './modules/'
MODULES = './modules/'

# How many processes should be parsing files at the same time?
# Note: This is a tradeoff between CPU power and disk I/O. More workers
# means higher CPU utilization, but disk I/O might become a limiting factor.
# Conversely: less workers might mean optimal disk I/O, but your CPU might
# be sitting idle...
# Example: CONSUMERS = 2
CONSUMERS = 1