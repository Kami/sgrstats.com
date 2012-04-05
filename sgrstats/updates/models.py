from django.db import models
from django_extensions.db.fields import AutoSlugField

class Update(models.Model):
    title = models.CharField(max_length = 150)
    title_slug = AutoSlugField(populate_from = 'title')
    date_fetched = models.DateTimeField(auto_now_add = True)
    body = models.TextField()
    thread_id = models.PositiveIntegerField()
    source = models.URLField()
    
    def __unicode__(self):
        return '%s' % (self.title)
    
    @models.permalink
    def get_absolute_url(self):
        return ('update_details', (), {'title_slug': self.title_slug})
