from django.contrib.sitemaps import Sitemap
from news.models import News
from articles.models import Article
from polls.models import Poll

class NewsSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5
    
    def items(self):
        return News.objects.all()
    
    def last_mod(self, obj):
        return obj.date_published
    
class ArticlesSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def items(self):
        return Article.objects.all()
    
    def last_mod(self, obj):
        return obj.date_published
    
class PollSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def items(self):
        return Poll.objects.all()
    
    def last_mod(self, obj):
        return obj.date_published