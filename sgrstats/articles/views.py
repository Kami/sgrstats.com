import datetime

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from articles.models import Article
from taxonomy.models import TaxonomyMap

from core.views import update_online_users

@update_online_users
def index(request):
    articles = Article.objects.all()[:10]
    
    return render_to_response('articles/index.html', {'articles': articles}, context_instance = RequestContext(request))

@update_online_users
def category(request, category_id):
    article_ids = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'article').values_list('object_id', flat = True)
    category_title = TaxonomyMap.objects.filter(term__id = category_id, type__type = 'Category', content_type__model = 'article')[0].term.term
    
    articles = Article.objects.filter(id__in = article_ids)
    
    return render_to_response('articles/category.html', {'category_id': category_id, 'category_title': category_title, 'articles': articles}, context_instance = RequestContext(request))

@update_online_users
def details(request, title_slug):
    article = get_object_or_404(Article, title_slug = title_slug)
    
    return render_to_response('articles/details.html', {'article': article}, context_instance = RequestContext(request))