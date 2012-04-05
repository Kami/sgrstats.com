"""
Horuly delete old online set keys.

Delete old set keys used for tracking online users from Redis database.
"""
import datetime
import redis

import sgrstats.core.views
from django_extensions.management.jobs import HourlyJob

class Job(HourlyJob):
    help = "Delete old set keys from Redis database"

    def execute(self):
        # Delete keys from previous hour (up to last 15 minutes)
        r = redis.Redis()
        
        now = datetime.datetime.now()
        minutes_ago  = now - datetime.timedelta(minutes = 15)
        hour_ago = minutes_ago - datetime.timedelta(hours = 1)
        
        for minute in range(0, 61):
            date = hour_ago + datetime.timedelta(minutes = minute)
            key = sgrstats.core.views._get_key_name(date)
            r.delete(key)
