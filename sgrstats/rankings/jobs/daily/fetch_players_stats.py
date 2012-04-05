"""
Daily rankings data update job.

Fetches and saves fresh objectives for all the users with a linked account.

Values from this document are later used for calculating the top data (top
player, map, class, weapon, ...).
"""
from django.db.models import Q
from sgrstats.stats.models import UserProfile
from django_extensions.management.jobs import DailyJob

from rankings.tasks import FetchPlayerStatsTask

class Job(DailyJob):
	help = "Adds tasks for fetching players statistics to the queue"

	def execute(self):
		# Add fetch jobs for all the players with a linked account to the job queue
		accounts = list(set(UserProfile.objects.filter(Q(account_id__isnull = False)) \
							  .values_list('account_id', 'user__id', 'user__username')))
		
		for account in accounts:
			FetchPlayerStatsTask.delay(account)
