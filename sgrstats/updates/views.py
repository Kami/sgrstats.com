from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from models import Update

from core.views import update_online_users

@update_online_users
def index(request):
    updates = Update.objects.all().order_by('-id')[:3]
    
    return render_to_response('updates/index.html', {'updates': updates}, context_instance = RequestContext(request))

@update_online_users
def details(request, title_slug):
    update = get_object_or_404(Update, title_slug = title_slug)
    
    return render_to_response('updates/details.html', {'update': update}, context_instance = RequestContext(request))