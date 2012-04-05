from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Deal
from taxonomy.models import TaxonomyMap

class TaxonomyMapInline(generic.GenericTabularInline):
    model = TaxonomyMap
    verbose_name = 'deal type'
    verbose_name_plural = 'deal types'

class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'get_type', 'price')
    search_fields = ['title', 'description']
    
    inlines = [TaxonomyMapInline]

admin.site.register(Deal, DealAdmin)