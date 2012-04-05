from django.contrib.syndication.views import Feed
from sgrstats.polls.models import Poll

class LatestPollsFeed(Feed):
    title = 'SGRstats.com polls'
    link = '/polls/'
    description = 'Latest polls from SGRstats.com - your primary source for Stargate Resistance related news, articles and player statistics'
    
    def items(self):
        return Poll.objects.all().order_by('-date_published')[:10]
    
    def item_title(self, item):
        return item.question
    
    def item_description(self, item):
        return item.description
    
    def item_author_name(self, item):
        return item.author.username
    
    def item_pubdate(self, item):
        return item.date_published