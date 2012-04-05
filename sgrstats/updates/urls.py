from django.conf.urls.defaults import *
from feeds import LatesUpdatesFeed

urlpatterns = patterns('',
    # Includes
    url(r'^$', 'updates.views.index', name = 'updates_index'),
    url(r'^feed/', LatesUpdatesFeed(), name = 'updates_feed'),
    url(r'^(?P<title_slug>.*?)/', 'updates.views.details', name = 'update_details'),
)
