from django.db import models

class PlainText(models.Model):
	HashID = models.AutoField(primary_key=True)
	Content = models.TextField(max_length=255)

class PDF(models.Model):
	Author = models.AutoField(primary_key=True)
	Organisation = models.TextField(max_length=255)
	Printed = models.TextField(max_length=255)
	Version = models.TextField(max_length=255)
	Content = models.TextField(max_length=255)
