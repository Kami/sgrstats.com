"""
Daily top values calculate job.

Note: Player statistics jobs should be finished around
01:00 and it's essential that this job runs after it.
"""

from django.db.models import Q
from sgrstats.stats.models import UserProfile
from django_extensions.management.jobs import DailyJob

from rankings.tasks import CalculateTopClassesTask
from rankings.tasks import CalculateTopMapsTask
from rankings.tasks import CalculateTopWeaponsTask

class Job(DailyJob):
	help = "Adds tasks for calculating the top values (to maps, weapon, ...) to the queue"
	
	def execute(self):
		CalculateTopClassesTask.delay()
		CalculateTopMapsTask.delay()
		CalculateTopWeaponsTask.delay()
