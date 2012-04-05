from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^top_player/', 'rankings.views.top_player', name = 'rankings_top_player'),
    url(r'^top_class/', 'rankings.views.top_class', name = 'rankings_top_class'),
    url(r'^top_map/', 'rankings.views.top_map', name = 'rankings_top_map'),
    url(r'^top_weapon/', 'rankings.views.top_weapon', name = 'rankings_top_weapon'),
)
