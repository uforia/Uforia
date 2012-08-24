#!/usr/bin/env python

from django.db import models

#This file creates the tables and columns for the data that is found by the different modules. Each class is a new table.
class PlainText(models.Model):
	HashID = models.AutoField(primary_key=True)
	Content = models.TextField(max_length=255)

class PDF(models.Model):
	Author = models.AutoField(primary_key=True)
	Organisation = models.TextField(max_length=255)
	Printed = models.TextField(max_length=255)
	Version = models.TextField(max_length=255)
	Content = models.TextField(max_length=255)
