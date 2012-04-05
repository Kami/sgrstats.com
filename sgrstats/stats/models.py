from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from static import CLASS_CATEGORIES

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique = True)
    
    account_id = models.IntegerField(blank = True, null = True)
    dynamic_signature = models.BooleanField(default = False)
    date_signature_generated = models.DateTimeField(blank = True, null = True)
    date_signature_last_checked = models.DateTimeField(blank = True, null = True)
    show_on_rankings = models.BooleanField(default = True)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user = instance)
        
post_save.connect(create_user_profile, sender = User)
        
class ClassRank(models.Model):
    title = models.CharField(max_length = 100)
    category = models.SmallIntegerField(choices = CLASS_CATEGORIES)
    exp_min = models.PositiveIntegerField()
    exp_max = models.PositiveIntegerField()
            
    def __unicode(self):
        return '%s (%d - %d EXP)' % (self.title, self.exp_min, self.exp_max)