"""
Daily players objectives and achievements update job.

Fetches fresh objectives and achievements from FireSky server and saves them to the database.
"""
import datetime

from django_extensions.management.jobs import DailyJob

class Job(DailyJob):
    help = "Fetch and update players objectives and achievements"

    def execute(self):
        pass
#        import sgrstats.stats.utils
#        sgrstats.stats.utils.update_players_data('update_both')
