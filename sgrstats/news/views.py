import datetime
import random

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.contrib.comments.views.comments import post_comment
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.utils.cache import _generate_cache_header_key, get_cache_key
from django.core.cache import cache

from django.db.models import Count
from django.contrib.comments.models import Comment
from news.models import News
from taxonomy.models import TaxonomyMap

from stats.views import _get_cache_key_name
from core.views import update_online_users

@update_online_users
def index(request):
    # Show news archive for current month
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    
    return archive(request, year, month)

@update_online_users
def archive(request, year = None, month = None):    
    if month is None and year is None:
        news = News.objects.all().order_by('-date_published')
        date = None
    elif month is None:
        year = int(year)
        
        if year < 2010 or year >= 2100:
            raise Http404()
    
        news = News.objects.filter(date_published__gte = datetime.date(year, 1, 1))
        date = datetime.date(year, 1, 1)
    else:
        year = int(year)
        month = int(month)
        
        if year < 2010 or year >= 2100 or month not in range(1,13):
            raise Http404()
        
        news = News.objects.filter(date_published__gte = datetime.date(int(year), int(month), 1), date_published__lte = datetime.date(int(year), int(month) + 1, 1))
        date = datetime.date(year, month, 1)
    
    month_year_list = get_available_month_year_pairs()
    return render_to_response('news/archive.html', {'news': news, 'month_year_list': month_year_list, \
                                                    'date': date, 'year': year, 'month': month}, \
                                                    context_instance = RequestContext(request))

@update_online_users
def details(request, title_slug):
    news = get_object_or_404(News, title_slug = title_slug)
    
    return render_to_response('news/details.html', {'news': news}, context_instance = RequestContext(request))

def comment_post_wrapper(request):
    if request.user.is_authenticated():
        if not (request.user.username == request.POST['name'] and \
               request.user.email == request.POST['email']):
            return HttpResponse("You registered user...trying to spoof a form...eh?")
        return post_comment(request)
    return HttpResponse("You anonymous cheater...trying to spoof a form?")

def comment_posted(request):
    try:
        comment_id = request.GET['c']
        comment = get_object_or_404(Comment, pk = comment_id)
        news = News.objects.get(pk = comment.content_object.pk)
        
        if news:
            return HttpResponseRedirect('%s#c%s' % (news.get_absolute_url(), comment_id))
    except KeyError:
        pass
    
    return HttpResponseRedirect('/')        

@update_online_users
def category(request, category_id):
    news_ids = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'news').values_list('object_id', flat = True)
    category_title = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'news')[0].term.term
    news = News.objects.filter(id__in = news_ids)
    
    return render_to_response('news/category.html', {'category_id': category_id, 'category_title': category_title, 'news': news}, context_instance = RequestContext(request))

# Helper functions
def get_available_month_year_pairs():
    key = _get_cache_key_name('news.archive', 'month_year_pairs')
    news = cache.get(key, False)
    
    if news != False:
        return news
    
    news = News.objects.all().order_by('date_published').values_list('date_published', flat = True)
    
    month_year_list = []
    for news in news:
        month = news.month
        year = news.year
        
        # Only one entry for each month / year pair is included
        exists = len([x for x in month_year_list if len(x) == 4 and (x[1] == month and x[2] == year)])
        
        if not exists:
            date = datetime.date(year, month, 1)
            news_count = News.objects.filter(date_published__month = month, \
                                         date_published__year = year).count()
            month_year_list.append((date, month, year, news_count))
    
    cache.set(key, month_year_list, 12 * 60 * 60)    
    return month_year_list 