from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User

class Poll(models.Model):
    question = models.CharField(max_length = 150)
    description = models.CharField(max_length = 250)
    date_published = models.DateTimeField(auto_now_add = True)
    enabled = models.BooleanField(default = True)
    author = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.question
    
    @models.permalink
    def get_absolute_url(self):
        return ('poll_results', (), {'poll_id': self.id})
    
    def get_total_vote_count(self):
        return self.choice_set.aggregate(Count('vote'))['vote__count']

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice = models.CharField(max_length = 80)
    
    def __unicode__(self):
        return self.choice
    
    def get_vote_percentage(self):
        total_vote_count = self.poll.choice_set.aggregate(Count('vote'))['vote__count']
        
        if total_vote_count == 0:
            return 0
        
        return int((self.vote_set.count() / float(total_vote_count)) * 100)

class Vote(models.Model):
    choice = models.ForeignKey(Choice)
    ip_address = models.IPAddressField()
    date_created = models.DateTimeField(auto_now_add = True)
    