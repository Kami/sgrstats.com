"""
Daily MongoDB database purge job.

Delets entries older then 1 day.
"""
import datetime
from sgrstats.settings import OLD_DATA_THRESHOLD

from django_extensions.management.jobs import DailyJob

class Job(DailyJob):
    help = "Purge old player objectives and achievements from MongoDB"

    def execute(self):
        pass
#        from mongodb import *
#        
#        diff = datetime.datetime.now() - datetime.timedelta(days = OLD_DATA_THRESHOLD)
#        database.players_objective_lists.remove({'date_retrieved': {'$lte': diff}})
#        database.players_achievement_lists.remove({'date_retrieved': {'$lte': diff}})
