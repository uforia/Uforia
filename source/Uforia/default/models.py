from django.db import models

class Hash(models.Model):
    	HashID = models.AutoField(primary_key=True) #Er is geen one-to-one relations
	MD5 = models.TextField(max_length=255)
	SHA1 = models.TextField(max_length=255)
	SHA256 = models.TextField(max_length=255)
	FileType = models.TextField(max_length=255)
	FileSize = models.CharField(max_length=255)
	
class Metadata(models.Model):
	HashID = models.AutoField(primary_key=True)
	Location = models.TextField(max_length=255)
	Name = models.TextField(max_length=255)
	MTimes = models.TextField(max_length=255)
	ATimes = models.TextField(max_length=255)
	CTimes = models.TextField(max_length=255)
	Owner = models.TextField(max_length=255)
	Groups = models.TextField(max_length=255)
	Permissions = models.TextField(max_length=255)