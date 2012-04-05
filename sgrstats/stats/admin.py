from django.contrib import admin

from models import ClassRank

class ClassRankAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'exp_min', 'exp_max')
    search_fields = ['title', 'category']
    
admin.site.register(ClassRank, ClassRankAdmin)