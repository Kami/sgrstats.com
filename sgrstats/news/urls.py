from django.conf.urls.defaults import *

from news.feeds import LatesNewsFeed, LatestNewsByCategoryFeed

urlpatterns = patterns('',
    # Includes
    url(r'^$', 'news.views.index', name = 'news_index'),
    url(r'^feed/', LatesNewsFeed(), name = 'news_feed'),
    url(r'^category/(?P<category_id>\d+)/feed/', LatestNewsByCategoryFeed(), name = 'news_category_feed'),
    url(r'^category/(?P<category_id>\d+)/', 'news.views.category', name = 'news_category'),
    url(r'^archive/(?P<year>\d{4})/(?P<month>\d{1,2})/', 'news.views.archive', name = 'news_archive_month'),
    url(r'^archive/(?P<year>\d{4})/', 'news.views.archive', name = 'news_archive_all'),
    url(r'^archive/', 'news.views.archive', name = 'news_archive_all'),
    url(r'^(?P<title_slug>.*?)/', 'news.views.details', name = 'news_details'),
)
