import random

from django.db import models

class Partner(models.Model):
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 250)
    website_url = models.URLField()
    banner_image = models.CharField(max_length = 100)
    visits = models.PositiveIntegerField(default = 0)
    enabled = models.BooleanField(default = True)
    
    def __unicoode__(self):
        return '%s - %s' % (self.name, self.website_url)