from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Update

class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_fetched')
    search_fields = ['title']

admin.site.register(Update, UpdateAdmin)