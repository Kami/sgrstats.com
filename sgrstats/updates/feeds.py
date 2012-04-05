from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from models import Update

class LatesUpdatesFeed(Feed):
    title = 'Latest SGR updates and patches'
    link = '/news/'
    description = 'Lates news about Stargate Resistance updates and patches'
    
    def items(self):
        return Update.objects.all().order_by('-id')[:10]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.body
    
    def item_pubdate(self, item):
        return item.date_fetched