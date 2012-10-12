#!/usr/bin/env python

# Enable debug output. Prints lots of information about internal workings.
# Note: Debug output is very noisy and should not be used in production.
DEBUG = False

# From which directory should Uforia start to scan?
# Example: STARTDIR = '/home/user/' 
STARTDIR = '/home/TESTDATA/'

# Where should Uforia find the modules to handle found MIME types?
# Note: You should not normally have to modify this!
# Example: MODULES = './modules/'
MODULEDIR = './modules/'

# Database configuration. The name should match the handler providing
# the appropriate Database class with setup() and store() methods.
# Example: DBTYPE = 'mysql'
DATABASEDIR = './databases/'
DBTYPE = 'mysql'
DBHOST = 'localhost'
DBUSER = 'uforia'
DBPASS = 'uforia'
DBNAME = 'uforia'

# How many processes should be parsing files at the same time?
# Note: This is a tradeoff between CPU power and disk I/O. More workers
# means higher CPU utilization, but disk I/O might become a limiting factor.
# Conversely: less workers might mean optimal disk I/O, but your CPU might
# be sitting idle...
# Example: CONSUMERS = 2
CONSUMERS = 2

# How many modules should be processing a file at the same time?
# Note: This is a tradeoff between CPU power and disk I/O. More workers
# means higher CPU utilization, but disk I/O might become a limiting factor.
# Conversely: less workers might mean optimal disk I/O, but your CPU might
# be sitting idle...
# Example: MODULES = 1
MODULES = 1
