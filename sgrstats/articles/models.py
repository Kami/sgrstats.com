from django.db import models
from markupfield.fields import MarkupField
from django.contrib.auth.models import User
from taxonomy.models import TaxonomyMap

class Article(models.Model):
    title = models.CharField(max_length = 250)
    title_slug = models.SlugField()
    date_published = models.DateTimeField(auto_now_add = True)
    author = models.ForeignKey(User)
    content = MarkupField(default_markup_type = 'markdown')

    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('article_details', (), {'title_slug': self.title_slug})
        
    def get_categories(self):
        categories = TaxonomyMap.objects.filter(object_id = self.pk, content_type__model = 'article')

        return categories
    
    def get_categories_flat(self):
        categories = TaxonomyMap.objects.filter(object_id = self.pk, content_type__model = 'article').values_list('term__term', flat = True)

        return categories
