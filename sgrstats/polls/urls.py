from django.conf.urls.defaults import *

from polls.feeds import LatestPollsFeed

urlpatterns = patterns('',
    # Includes
    url(r'^$', 'polls.views.index', name = 'polls_index'),
    url(r'^feed/$', LatestPollsFeed(), name = 'polls_feed'),
    url(r'^(?P<poll_id>\d+)/', 'polls.views.details', name = 'poll_details'),
    url(r'^vote/(?P<poll_id>\d+)/', 'polls.views.vote', name = 'poll_vote'),
    url(r'^results/(?P<poll_id>\d+)/(?P<choice_id>\d+)/', 'polls.views.results', name = 'poll_results_choice'),
    url(r'^results/(?P<poll_id>\d+)/', 'polls.views.results', name = 'poll_results'),
)