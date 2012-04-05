from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Partner

class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'website_url', 'enabled', 'visits')
    search_fields = ['name', 'website_url']

admin.site.register(Partner, PartnerAdmin)