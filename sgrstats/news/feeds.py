from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from news.models import News
from taxonomy.models import TaxonomyMap

class LatesNewsFeed(Feed):
    title = 'SGRstats.com news'
    link = '/news/'
    description = 'Latest news from SGRstats.com - your primary source for Stargate Resistance related news, articles and player statistics'
    
    def items(self):
        return News.objects.all().order_by('-date_published')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.excerpt
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.date_published
    
    def item_categories(self, item):
        return item.get_categories_flat()
    
class LatestNewsByCategoryFeed(Feed):
    description = 'Latest news from SGRstats.com - your primary source for Stargate Resistance related news, articles and player statistics'
    
    def title(self, obj):
        return 'SGRstats.com news in category "%s"' % obj[1]
    
    def link(self, obj):
        return reverse('news_category', args = (obj[0],))
    
    def get_object(self, request, category_id):
        news_ids = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'news').values_list('object_id', flat = True)
        category_title = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'news')[0].term.term
        
        return (category_id, category_title, news_ids)
    
    def items(self, obj):
        return News.objects.filter(id__in = obj[2]).order_by('-date_published')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.excerpt
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.date_published
    
    def item_categories(self, item):
        return item.get_categories_flat()