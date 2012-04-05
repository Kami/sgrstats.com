from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^visit/(?P<deal_id>\d+)/', 'deals.views.visit', name = 'deal_visit'),
)