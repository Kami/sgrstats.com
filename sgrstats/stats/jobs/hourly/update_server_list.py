"""
5 minutes server list update job.

Fetches fresh server list from FireSky server and save it to the database.
"""

from django_extensions.management.jobs import HourlyJob

class Job(HourlyJob):
    help = "Fetch and update server list"

    def execute(self):
        import sgrstats.stats.utils
        slu = sgrstats.stats.utils.ServerListUtils()
        slu.update_server_list()
        
