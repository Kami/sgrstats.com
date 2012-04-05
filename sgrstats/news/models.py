from django.db import models
from markupfield.fields import MarkupField
from django.contrib.auth.models import User
from taxonomy.models import TaxonomyMap
    
class News(models.Model):
    title = models.CharField(max_length = 250)
    title_slug = models.SlugField()
    date_published = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User)
    excerpt = MarkupField(default_markup_type = 'markdown')
    body = MarkupField(default_markup_type = 'markdown', blank = True)
    
    class Meta():
        verbose_name_plural = 'news'
        
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('news_details', (), {'title_slug': self.title_slug})
        
    def get_categories(self):
        categories = TaxonomyMap.objects.filter(object_id = self.pk, content_type__model = 'news')

        return categories
    
    def get_categories_flat(self):
        categories = TaxonomyMap.objects.filter(object_id = self.pk, content_type__model = 'news').values_list('term__term', flat = True)

        return categories