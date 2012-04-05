import random

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from deals.models import Deal
from taxonomy.models import TaxonomyMap

def visit(request, deal_id = None):
    deal = get_object_or_404(Deal, pk = deal_id)
    
    deal.visits += 1
    deal.save()
    
    return HttpResponseRedirect(deal.url)

def get_random_deal(request):
    """ Returns a random deal.
        
    If a user is not-logged in, game or random expansion deal is displayed
    and if user is logged in, random expansion deal is displayed."""
    
    if request.user.is_authenticated():
        deal_ids = TaxonomyMap.objects.filter(term__term = 'Expansion', type__type = 'Deal type').values_list('object_id', flat = True)
    else:
        deal_ids = TaxonomyMap.objects.filter(type__type = 'Deal type').values_list('object_id', flat = True)
    
    deal_id = random.sample(deal_ids, 1)[0]
    deal = Deal.objects.get(id = deal_id)
    type = TaxonomyMap.objects.get(object_id = deal_id, content_type__model = 'deal').type.type
    
    return (deal, type)