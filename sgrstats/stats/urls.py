from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page

import stats.views

# Redirect old now obsolete urls
urlpatterns = patterns('django.views.generic.simple',
    (r'^(?P<account_id>\d+)/', 'redirect_to', {'url': '/player_stats/summary/%(account_id)s', 'permanent': True}),
)

urlpatterns += patterns('',
    url(r'^summary/(?P<account_id>\d+)/', 'stats.views.stats', {'what': 'summary'}, name = 'stats_summary'),
    url(r'^kills/(?P<account_id>\d+)/', 'stats.views.stats', {'what': 'kills'}, name = 'stats_kills'),
    url(r'^classes/(?P<account_id>\d+)/', 'stats.views.stats', {'what': 'classes'}, name = 'stats_classes'),
    url(r'^maps/(?P<account_id>\d+)/', 'stats.views.stats', {'what': 'maps'}, name = 'stats_maps'),
    url(r'^achievements/(?P<account_id>\d+)/', 'stats.views.stats', {'what': 'achievements'}, name = 'stats_achievements'),

    #url(r'^leaderboards/(?P<account_id>\d+)/', 'stats.views.leaderboards', name = 'stats_leaderboards'),
    
    url(r'^stats/summary/(?P<account_id>\d+)/', 'stats.views.summary', name = 'stats_summary_data'),
    url(r'^stats/kills/(?P<account_id>\d+)/', 'stats.views.kills', name = 'stats_kills_data'),
    url(r'^stats/classes/(?P<account_id>\d+)/', 'stats.views.classes', name = 'stats_classes_data'),
    url(r'^stats/maps/(?P<account_id>\d+)/', 'stats.views.maps', name = 'stats_maps_data'),
    url(r'^stats/achievements/(?P<account_id>\d+)/', 'stats.views.achievements', name = 'stats_achievements_data'),
    
    url(r'^$', 'stats.views.index', name = 'stats_index'),
)
