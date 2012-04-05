from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'partners.views.index', name = 'partners_index'),
    url(r'^visit/(?P<partner_id>\d+)/', 'partners.views.visit', name = 'partners_visit'),
)