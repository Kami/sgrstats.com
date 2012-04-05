import os
import sys

from django.conf.urls.defaults import *
from django.views.decorators.cache import cache_page
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from sgrstats.settings import DEBUG

import sgrstats.stats.views

from sitemaps import NewsSitemap, ArticlesSitemap, PollSitemap
from django.contrib.sitemaps import FlatPageSitemap

reverse_lazy = lazy(reverse, unicode)

admin.autodiscover()

site_media = os.path.join(os.path.dirname(__file__), '../static/site_media')
admin_media = os.path.join(os.path.dirname(__file__), '../static/admin_media')

sitemaps = {
    'news': NewsSitemap,
    'articles': ArticlesSitemap,
    'polls': PollSitemap,
    'flatpages': FlatPageSitemap
}

urlpatterns = patterns('',
    # Redirect old now obsolete urls
    url(r'^server_list/', 'django.views.generic.simple.redirect_to', {'url': reverse_lazy('stats_servers'), 'permanent': True}),
    url(r'^player_achievements/(?P<account_id>\d+)/', 'django.views.generic.simple.redirect_to', {'url': '/player_stats/achievements/%(account_id)s', 'permanent': True}),
    
    # Applications
    (r'^$', 'sgrstats.core.views.index'),
    
    (r'^accounts/', include('sgrstats.accounts.urls')),
    (r'^player_stats/', include('sgrstats.stats.urls')),
    (r'^rankings/', include('sgrstats.rankings.urls')),
    url(r'^servers/', 'sgrstats.stats.views.servers', name = 'stats_servers'),
    (r'^articles/', include('sgrstats.articles.urls')),
    (r'^news/', include('sgrstats.news.urls')),
    (r'^updates/', include('sgrstats.updates.urls')),
    (r'^polls/', include('sgrstats.polls.urls')),
    (r'^partners/', include('sgrstats.partners.urls')),
    (r'^deals/', include('sgrstats.deals.urls')),
    url(r'^captcha/', include('captcha.urls')),
    #(r'^api/', include('sgrstats.api.urls')),
    
    # Third-party
    (r'^comments/post/$', 'sgrstats.news.views.comment_post_wrapper'),
    (r'^comments/posted/$', 'sgrstats.news.views.comment_posted'),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/',  'django.contrib.auth.views.login', {'redirect_if_logged_in': '/'}, name = 'auth_login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}, name = 'auth_logout'),
    url(r'^accounts/register/$', 'registration.views.register', {'backend': 'sgrstats.accounts.forms.CaptchaRegistrationBackend'}, name = 'registration_register'),
    (r'^accounts/', include('registration.urls')),
    (r'^grappelli/', include('grappelli.urls')),
    
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
)

if DEBUG:
    urlpatterns += patterns('',
    # Media
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media}),
        (r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': admin_media}),
    )