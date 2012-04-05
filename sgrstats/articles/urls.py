from django.conf.urls.defaults import *

from articles.feeds import LatestArticlesFeed, LatestArticlesByCategoryFeed

urlpatterns = patterns('',
    # Includes
    url(r'^$', 'articles.views.index', name = 'articles_index'),
    url(r'^feed/', LatestArticlesFeed(), name = 'articles_feed'),
    url(r'^category/(?P<category_id>\d+)/feed/', LatestArticlesByCategoryFeed(), name = 'articles_category_feed'),
    url(r'^category/(?P<category_id>\d+)/', 'articles.views.category', name = 'articles_category'),
    url(r'^(?P<title_slug>.*?)/', 'articles.views.details', name = 'article_details'),
)
