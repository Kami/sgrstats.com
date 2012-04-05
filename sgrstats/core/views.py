import datetime

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.contrib.comments.views.comments import post_comment
from django.template import RequestContext
from django.core.urlresolvers import reverse

from polls.views import get_user_vote_count
from deals.views import get_random_deal

from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from news.models import News
from articles.models import Article
from polls.models import Poll
from partners.models import Partner
from updates.models import Update
from deals.models import Deal

import redis

# Decorators
def update_online_users(function = None):
    """ Update online user decorator. """
    def _dec(view_func):  
        def _view(request, *args, **kwargs): 
            if request.user.is_authenticated():
                r = redis.Redis()
                user_id = request.user.id
                r.sadd(_get_key_name(), user_id)

            return view_func(request, *args, **kwargs)
        
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__
        
        return _view
    
    if function is None:
        return _dec
    else:
        return _dec(function)

@update_online_users
def index(request):  
    news = News.objects.all().order_by('-date_published')[:5]
    poll = Poll.objects.latest('date_published')
    articles = Article.objects.order_by('-date_published')[:3]
    older_polls = Poll.objects.all().order_by('-date_published')[1:4]
    partners = Partner.objects.filter(enabled = True).order_by('?')[:5]
    latest_update = Update.objects.all().order_by('-id')[:1]
    vote_count = poll.choice_set.aggregate(Count('vote'))['vote__count']
    recently_online = get_recently_online_users()
    
    random_deal = Deal.objects.get_random_deal(request.user.is_authenticated())
    deal = random_deal[0]
    deal_type = random_deal[1]
    
    if get_user_vote_count(poll.id, request.META['REMOTE_ADDR']) >= 1:
        # User already votes in this poll
        poll_template = 'polls/poll_results.html'
    else:
        poll_template = 'polls/poll_details.html'
    
    return render_to_response('index.html', {'news': news, 'articles': articles, 'poll': poll, \
                                             'poll_template': poll_template, 'vote_count': vote_count, \
                                             'older_polls': older_polls, 'partners': partners, \
                                             'latest_update': latest_update[0], \
                                             'recently_online': recently_online, \
                                             'deal': deal, \
                                             'deal_type': deal_type}, \
                                              context_instance = RequestContext(request))
    
# Helper functions    
def get_recently_online_users():
    """ Returns a list of (username, account_id) tuples. """
    users = User.objects.filter(id__in = get_recently_online_user_ids())
    users_list = [(user.username, user.get_profile().account_id) for user in users]
    
    return users_list

def get_recently_online_user_ids():
    """ Returns a list of users online in last 15 minutes. """
    r = redis.Redis()
    
    return list(r.sunion(_get_keys_in_last_15_minutes()))

def _get_keys_in_last_15_minutes():
    """ Returns name of the keys for sets created in last 15 minutes. """
    now = datetime.datetime.now()
    keys = [_get_key_name(date) for date in [now - datetime.timedelta(minutes = min) for min in range(0,16)]]
    
    return keys

def _get_key_name(date = None):
    """ Returns a key name for a given date.
      If no date object is given, the current date is used. """
    if date is None:
        date = datetime.datetime.now()
    
    time = date.strftime('%H:%M')
    key = 'online.users.%s' % (time)
    
    return key