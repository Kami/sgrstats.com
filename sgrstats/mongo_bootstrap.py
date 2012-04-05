# Setup Django environment
from django.core.management import setup_environ 
import settings 
setup_environ(settings)

import pymongo

from mongodb import connection, database
from pymongo import ASCENDING, DESCENDING

# Create collection indexes

database.servers.create_index([('named', ASCENDING)])

database.players_objective_lists.create_index([('date_retrieved', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_ExperiencePointsEarned', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_KillsTotal', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_KilledTotal', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_ShotsFired', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_ShotsHit', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_WinsTotal', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_LossesTotal', DESCENDING)])
database.players_objective_lists.create_index([('SGR_Account_TimePlayedTotal', DESCENDING)])

database.players_achievement_lists.create_index([('date_retrieved', DESCENDING)])