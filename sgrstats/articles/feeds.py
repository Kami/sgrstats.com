from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from articles.models import Article
from taxonomy.models import TaxonomyMap

class LatestArticlesFeed(Feed):
    title = 'SGRstats.com articles'
    link = '/articles/'
    description = 'Latest articles from SGRstats.com - your primary source for Stargate Resistance related news, articles and player statistics'
    
    def items(self):
        return Article.objects.all().order_by('-date_published')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.content
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.date_published
    
    def item_categories(self, item):
        return item.get_categories_flat()
    
class LatestArticlesByCategoryFeed(Feed):
    description = 'Latest articles from SGRstats.com - your primary source for Stargate Resistance related news, articles and player statistics'
    
    def title(self, obj):
        return 'SGRstats.com articles in category "%s"' % obj[1]
    
    def link(self, obj):
        return reverse('articles_category', args = (obj[0],))
    
    def get_object(self, request, category_id):
        article_ids = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'article').values_list('object_id', flat = True)
        category_title = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'article')[0].term.term
        
        return (category_id, category_title, article_ids)
    
    def items(self, obj):
        return Article.objects.filter(id__in = obj[2]).order_by('-date_published')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.content
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.date_published
    
    def item_categories(self, item):
        return item.get_categories_flat()