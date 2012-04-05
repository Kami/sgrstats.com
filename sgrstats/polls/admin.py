from django.contrib import admin
from models import Poll, Choice, Vote

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'description', 'date_published', 'enabled')
    search_fields = ['question'', description']
    
    inlines = [ChoiceInline]
    
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('poll', 'choice')
    search_fields = ['choice']
    
class VoteAdmin(admin.ModelAdmin):
    list_display = ('choice', 'ip_address', 'date_created')
    search_fields = ['choice', 'ip_address']

admin.site.register(Poll, PollAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Vote, VoteAdmin)