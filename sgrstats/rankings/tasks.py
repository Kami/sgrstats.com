# -*- coding: utf-8 -*-
# Python
import datetime
import urllib2
import re

from urllib2 import URLError, HTTPError
from xml.dom import minidom
from lxml import etree
from pymongo.errors import OperationFailure
from pymongo.code import Code

# Django
from mongodb import *
from sgrstats.static import *

# Celery
from celery.task import Task
from celery.registry import tasks
from pymongo.errors import PyMongoError

class FetchPlayerStatsTask(Task):
	ignore_result = True
	max_retries = 30
	default_retry_delay = 3 * 60 # Retry in 3 minutes
	
	def run(self, user_data = None, **kwargs):
		""" Fetches and saves player's stats into the MongoDB collection. """
		objectives_to_fetch = ACCOUNT_OBJECTIVES_ALL + OBJECTIVES_MAPS_ALL + OBJECTIVES_CLASSES_ALL\
						 + OBJECTIVES_WEAPONS_ALL
	
		# When updating player data, user_data is a triple (account_id, user_id, username)
		# account_id - firesky account id, user_id - website account user id
		# username - website account username
		date = datetime.datetime.now()
		today = date.date()
		date_value = "%s-%s-%s" % (today.year, today.month, today.day)

		account_id, user_id, username = user_data
		
		try:
			player_objectives = self.fetch_player_objective_list(account_id)
		except (IOError, URLError), exc:
			# try to retry the task later on
			self.retry((user_data,), kwargs, exc = exc)
			return

		dom = etree.fromstring(player_objectives)
		
		# Loop over all the available objectives
		empty_count = 0
		player_data = {'account_id': account_id, 'user_id': user_id,
						'username': username, 'date_short': date_value,
						'date_full': date, 'data': {}}
		
		player_objectives = player_data['data']
		for node in dom.iter('{%s}Objective' % (OBJECTIVE_LIST_NS)):
			objective_id = node.attrib.get('ObjectiveID', '')
			objective_value = node.attrib.get('ProgressValue', '')
			
			if objective_id in objectives_to_fetch:
				try:
					value = int(objective_value)
				except ValueError:
					value = 0
				
				player_objectives['%s' % (objective_id)] = value
		
			if objective_value == '':
				empty_count += 1
		
		if empty_count == len(player_objectives) - 2:
			# All the values are empty, this player does not exist
			return
		
		# Calculate K/D and hit ratio
		types = ['Account']
		for type in types:
			try:
				player_objectives['%s_%s_%s' % ('SGR', type, 'KillDeathRatio')] = float(player_objectives['%s_%s_%s' % ('SGR', type, 'KillsTotal')]) / float(player_objectives['%s_%s_%s' % ('SGR', type, 'KilledTotal')])
				player_objectives['%s_%s_%s' % ('SGR', type, 'HitRatio')] = (float(player_objectives['%s_%s_%s' % ('SGR', type, 'ShotsHit')]) / float(player_objectives['%s_%s_%s' % ('SGR', type, 'ShotsFired')])) * 100
			except (ZeroDivisionError, KeyError):
				player_objectives['%s_%s_%s' % ('SGR', type, 'KillDeathRatio')] = 0
				player_objectives['%s_%s_%s' % ('SGR', type, 'HitRatio')] = 0
		
		# Total account values for Leonops map (arena game type) are not recorded, so we need to
		# calculate them manually
		try:
			player_objectives['SGR_Account_WinsOnArena'] = sum([int(player_objectives['SGR_%s_WinsOnArena' % (type)]) for type in types[3:]])
		except:
			pass
		
		try:
			player_objectives['SGR_Account_LossesOnArena'] = sum([int(player_objectives['SGR_%s_LossesOnArena' % (type)]) for type in types[3:]])
		except:
			pass
		
		try:
			database.rankings_data.save(player_data, safe = True)
		except (OperationFailure), exc:
			# Failed inserting document in the collection, retry later
			self.retry((user_data,), kwargs, exc = exc)
	
	def fetch_player_objective_list(self, account_id):
		""" Fetch player objectives. """
		
		post_data = '''<ns2:Registration xmlns:ns1="http://www.cheyenneme.com/xml/cmebase" xmlns:ns2="http://www.cheyenneme.com/xml/registration"><ns2:Service><ns2:AccountObjectiveGet><ns2:Request AccountID="''' + str(account_id) + '''" /></ns2:AccountObjectiveGet></ns2:Service></ns2:Registration>'''
		request = urllib2.Request(OBJECTIVE_LIST_URL, data = post_data, headers = {
																 'User-Agent': USER_AGENT,
																 'Content-Type': 'text/plain',
																 })
		
		response = urllib2.urlopen(request, timeout = 6)
		return response.read()
	
class CalculateTopClassesTask(Task):
	ignore_result = True
	max_retries = 5
	default_retry_delay = 2 * 60
	
	def run(self, **kwargs):
		# Map function
		emit_string = ''
		for objective in OBJECTIVES_CLASSES_ALL:
			emit_string += 'emit("%s", this.data.%s);' % (objective, objective)
			
		map = Code("function() { %s }" % (emit_string))
		
		# Reduce function
		reduce = Code("function(key, values) {"
					  "  var total = 0;"
					  "  for (var i = 0; i < values.length; i++) {"
					  "	total += values[i];"
					  "  }"
					  "  return total;"
					  "}")
		
		today = datetime.datetime.now().date()
		date = "%s-%s-%s" % (today.year, today.month, today.day)
		
		# Calculate the result (map & reduce)
		query = {'date_short': date}
		result = database.rankings_data.map_reduce(map, reduce, query = query)
		
		results = {}
		for doc in result.find():
			objective = doc['_id']
			value = doc['value']
			
			results[objective] = value
		
		# Save the cumulatives in the top_classes collection
		# Entry _id contains the current date (YYYY-mm-dd)
		try:
			database.top_classes.save({'_id': date, \
								'data': results}, safe = True)
		except (OperationFailure), exc:
			self.retry((), kwargs, exc = exc)
			
class CalculateTopMapsTask(Task):
	ignore_result = True
	max_retries = 5
	default_retry_delay = 2 * 60
	
	def run(self, **kwargs):
		# Map function
		emit_string = ''
		for objective in OBJECTIVES_MAPS_ALL:
			emit_string += 'emit("%s", this.data.%s);' % (objective, objective)
			
		map = Code("function() { %s }" % (emit_string))
		
		# Reduce function
		reduce = Code("function(key, values) {"
					  "  var total = 0;"
					  "  for (var i = 0; i < values.length; i++) {"
					  "	total += values[i];"
					  "  }"
					  "  return total;"
					  "}")
		
		today = datetime.datetime.now().date()
		date = "%s-%s-%s" % (today.year, today.month, today.day)
		
		# Calculate the result (map & reduce)
		query = {'date_short': date}
		result = database.rankings_data.map_reduce(map, reduce, query = query)
		
		results = {}
		for doc in result.find():
			objective = doc['_id']
			value = doc['value']
			
			results[objective] = value

		try:
			database.top_maps.save({'_id': date, \
								'data': results}, safe = True)
		except (OperationFailure), exc:
			self.retry((), kwargs, exc = exc)
			
class CalculateTopWeaponsTask(Task):
	ignore_result = True
	max_retries = 5
	default_retry_delay = 2 * 60
	
	def run(self, **kwargs):
		# Map function
		emit_string = ''
		for objective in OBJECTIVES_WEAPONS_ALL:
			emit_string += 'emit("%s", this.data.%s);' % (objective, objective)
			
		map = Code("function() { %s }" % (emit_string))
		
		# Reduce function
		reduce = Code("function(key, values) {"
					  "  var total = 0;"
					  "  for (var i = 0; i < values.length; i++) {"
					  "	total += values[i];"
					  "  }"
					  "  return total;"
					  "}")
		
		today = datetime.datetime.now().date()
		date = "%s-%s-%s" % (today.year, today.month, today.day)
		
		# Calculate the result (map & reduce)
		query = {'date_short': date}
		result = database.rankings_data.map_reduce(map, reduce, query = query)
		
		results = {}
		for doc in result.find():
			objective = doc['_id']
			value = doc['value']
			
			results[objective] = value

		try:
			database.top_weapons.save({'_id': date, \
								'data': results}, safe = True)
		except (OperationFailure), exc:
			self.retry((), kwargs, exc = exc)