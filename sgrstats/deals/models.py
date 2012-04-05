import random

from django.db import models
from taxonomy.models import TaxonomyTerm, TaxonomyMap

class DealManager(models.Manager):
    def get_random_deal(self, logged_in = False):
        """ Returns a random deal.
        
        If a user is not-logged in, game or random expansion deal is displayed
        and if user is logged in, random expansion deal is displayed."""
    
        if logged_in:
            deal_ids = TaxonomyMap.objects.filter(term__term = 'Expansion', type__type = 'Deal type').values_list('object_id', flat = True)
        else:
            deal_ids = TaxonomyMap.objects.filter(term__term = 'Game',type__type = 'Deal type').values_list('object_id', flat = True)
        
        deal_id = random.sample(deal_ids, 1)[0]
        deal = Deal.objects.get(id = deal_id)
        type = TaxonomyMap.objects.get(object_id = deal_id, content_type__model = 'deal').term.term.lower()
        
        return (deal, type)

class Deal(models.Model):
    title = models.CharField(max_length = 150)
    description = models.CharField(max_length = 250)
    image_thumb = models.CharField(max_length = 150)
    image_large = models.CharField(max_length = 150)
    url = models.URLField()
    price = models.FloatField()
    visits = models.PositiveIntegerField(default = 0)
    enabled = models.BooleanField(default = True)
    objects = DealManager()
    
    def __unicoode__(self):
        return '%s (%d)' % (self.name, self.price)
    
    def get_type(self):
        type = TaxonomyTerm.objects.filter(taxonomymap__object_id = self.pk, taxonomymap__content_type__model = 'deal')
        type = type[0].term
        
        return type