from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from partners.models import Partner

from core.views import update_online_users

@update_online_users
def index(request):
    partners = Partner.objects.filter(enabled = True)
    
    return render_to_response('partners/index.html', {'partners': partners}, context_instance = RequestContext(request))

@update_online_users
def visit(request, partner_id = None):
    partner = get_object_or_404(Partner, pk = partner_id)
    
    partner.visits += 1
    partner.save()
    
    return HttpResponseRedirect(partner.website_url)