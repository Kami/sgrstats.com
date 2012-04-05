from django.contrib import admin
from django.contrib.contenttypes import generic

from models import News
from taxonomy.models import TaxonomyMap

class TaxonomyMapInline(generic.GenericTabularInline):
    model = TaxonomyMap
    verbose_name = 'category'
    verbose_name_plural = 'categories'

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'get_categories', 'date_published')
    search_fields = ['title']
    
    prepopulated_fields = {'title_slug': ('title',)}
    inlines = [TaxonomyMapInline]

admin.site.register(News, NewsAdmin)