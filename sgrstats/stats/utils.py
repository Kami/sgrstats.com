# -*- coding: utf-8 -*-
# Python
import threading
import datetime
import urllib2
import re

from urllib2 import URLError, HTTPError
from xml.dom import minidom 
from lxml import etree

# Django
from mongodb import *

from sgrstats.static import *
from django.db.models import Q
from sgrstats.stats.models import UserProfile

# Constants
MAX_THREADS = 8

class ServerListUtils(object):
	def fetch_server_list(self):
		""" Fetch the currently active servers. """

		request = urllib2.Request(SERVER_LIST_URL, headers = {'User-Agent': USER_AGENT})
		
		try:
			response = urllib2.urlopen(request, timeout = 5)
		except Exception, e:
			# Failed to reach a server / server problems
			return None
		
		return response.read()
	
	def update_server_list(self, return_fetched_data = False):
		""" Update the server list in the database (delete old and save fetched ones). """
		
		servers = self.fetch_server_list()
		
		if not servers:
			return

		dom = minidom.parseString(servers)
		date = datetime.datetime.now()
		
		server_list = []
		total_player_count = 0
		for node in dom.getElementsByTagName('Server'):
			name = node.getAttribute('ServerName')
			address = node.getAttribute('ServerConnectionString')
			map = node.getAttribute('MapName')
			game_type = node.getAttribute('GameType')
			sgc_player_count = int(node.getAttribute('SGCPop'))
			sl_player_count = int(node.getAttribute('SLPop'))
			
			# Temporary disabled the location, since all the servers are currently location in US
			# ip_location = ip_to_location(address.split(':')[0])
			# (country, country_code, city) = ip_to_location(address.split(':')[0])
			
			(country, country_code, city) = ('United Stats', 'us', 'Plano, TX')
			total_player_count += int(node.getAttribute('SGCPop')) + int(node.getAttribute('SLPop'))
			
			server = {'date_retrieved': date, 'name': name, 'address': address, 'location': list((country, country_code, city)), 'map': map, 'game_type': game_type, 'sgc_player_count': sgc_player_count, 'sl_player_count': sl_player_count}
			server_list.append(server)
		
		if len(server_list) > 0:
			# Remove old servers
			database.servers.remove()
				
		database.servers.insert(server_list)
		
		if return_fetched_data:
			return server_list
	
class PlayerUtils(threading.Thread):
	def __init__(self, account_ids = None, action = 'update_objectives'):
		self.account_ids = account_ids
		self.action = action
		threading.Thread.__init__(self)
		
	def run(self):
		if self.action == 'update_objectives':
			self.update_players_objective_lists()
		elif self.action == 'update_achievements':
			self.update_players_achievement_lists()
		elif self.action == 'update_rankings_data':
			self.update_rankings_data()
		
	def fetch_player_objective_list(self, account_id):
		""" Fetch player objectives. """

		post_data = '''<ns2:Registration xmlns:ns1="http://www.cheyenneme.com/xml/cmebase" xmlns:ns2="http://www.cheyenneme.com/xml/registration"><ns2:Service><ns2:AccountObjectiveGet><ns2:Request AccountID="''' + str(account_id) + '''" /></ns2:AccountObjectiveGet></ns2:Service></ns2:Registration>'''
		request = urllib2.Request(OBJECTIVE_LIST_URL, data = post_data, headers = {
																 'User-Agent': USER_AGENT,
																 'Content-Type': 'text/plain',
																 })

		try:
			response = urllib2.urlopen(request, timeout = 5)
		except Exception:
			return None

		return response.read()
	
	def fetch_player_achievement_list(self, account_id):
		""" Fetch player achievements. """
		
		post_data = '''<ns2:Registration xmlns:ns1="http://www.cheyenneme.com/xml/cmebase" xmlns:ns2="http://www.cheyenneme.com/xml/registration"><ns2:Service><ns2:AccountAchievementGet><ns2:Request AccountID="''' + str(account_id) + '''" /></ns2:AccountAchievementGet></ns2:Service></ns2:Registration>'''
		request = urllib2.Request(ACHIEVEMENT_LIST_URL, data = post_data, headers = {
																 'User-Agent': USER_AGENT,
																 'Content-Type': 'text/plain',
																 })

		try:
			response = urllib2.urlopen(request, timeout = 5)
		except Exception:
			return None

		return response.read()
	
	def update_players_objective_lists(self, return_fetched_data = False):
		""" Fetch the players objective lists and save it into the database.
		
			return_fetched_data -- If true, return the saved data
		"""
		
		if not self.account_ids:
			return
		
		date = datetime.datetime.now()

		players_objectives = []
		for account_id in self.account_ids:
			player_objectives = self.fetch_player_objective_list(account_id)
			
			if not player_objectives:
				if len(self.account_ids) == 1 and return_fetched_data:
					# FireSky servers are offline or unavailable
					return False
				continue
			
			dom = etree.fromstring(player_objectives)
			
			# Loop over all the available objectives
			empty_count = 0
			player_objectives = {'_id': int(account_id), 'date_retrieved': date}
			for node in dom.iter('{%s}Objective' % (OBJECTIVE_LIST_NS)):
				objective_id = node.attrib.get('ObjectiveID', '')
				objective_value = node.attrib.get('ProgressValue', '')
				
				if objective_value != '':
					player_objectives[objective_id] = int(objective_value)
				else:
					player_objectives[objective_id] = 0
					empty_count += 1

			if empty_count == len(player_objectives) - 2:
				# All the values are empty, this player does not exist
				continue
			
			# Calculate K/D and hit ratio
			types = ['Account', 'SGC', 'SystemLords', 'Soldier', 'Commando', 'Scientist', 'Goauld', 'Jaffa', 'Ashrak']
			for type in types:
				try:
					player_objectives['%s_%s_%s' % ('SGR', type, 'KillDeathRatio')] = float(player_objectives['%s_%s_%s' % ('SGR', type, 'KillsTotal')]) / float(player_objectives['%s_%s_%s' % ('SGR', type, 'KilledTotal')])
					player_objectives['%s_%s_%s' % ('SGR', type, 'HitRatio')] = (float(player_objectives['%s_%s_%s' % ('SGR', type, 'ShotsHit')]) / float(player_objectives['%s_%s_%s' % ('SGR', type, 'ShotsFired')])) * 100
				except ZeroDivisionError:
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
			
			database.players_objective_lists.save(player_objectives)
			players_objectives.append(player_objectives)
				
		if return_fetched_data:
			return players_objectives[0] if len(players_objectives) == 1 else players_objectives

	def update_players_achievement_lists(self, return_fetched_data = False):
		""" Fetch the players achievement lists and save them into the database.
			return_fetched_data -- If true, return the saved data
		"""
		
		if not self.account_ids:
			return
		
		date = datetime.datetime.now()

		players_achievements = []
		for account_id in self.account_ids:
			player_achievements = self.fetch_player_achievement_list(account_id)
			
			if not player_achievements:
				if len(self.account_ids) == 1 and return_fetched_data:
					# FireSky servers are offline or unavailable
					return False
				continue
			
			dom = etree.fromstring(player_achievements)

			# Loop over all the available objectives
			player_achievements = {'_id': int(account_id), 'date_retrieved': date, 'achievements': []}
			completed_achievements_count = 0
			for node in dom.iter('{%s}Achievement' % (ACHIEVEMENT_LIST_NS)):
				id = node.attrib.get('AchievementID', '')
				title = node.attrib.get('AchievementTitle', '')
				name = node.attrib.get('AchievementName', '')
				description = node.attrib.get('AchievementDesc', '')
				points = node.attrib.get('AchievementPoints', '')
				category = node.attrib.get('AchievementCategory', '')
				completed_on = node.attrib.get('CompleteOn', '')
				
				if completed_on:
					completed_achievements_count += 1
				
				player_achievements['achievements'].append({'id': int(id), 'title': title, 'name': name, 'description': description, 'points': points, 'category': category, 'completed_on': completed_on})

			player_achievements['total_count'] = len(player_achievements['achievements'])
			player_achievements['completed_count'] = completed_achievements_count
			# Save players achievements
			database.players_achievement_lists.save(player_achievements)
			players_achievements.append(player_achievements)
				
		if return_fetched_data:
			return players_achievements[0] if len(players_achievements) == 1 else players_achievements
		
	def update_rankings_data(self):
		""" Fetches and saves the data which is needed for rankings (top player, class, map, ...) for all
		users with a linked account. """
		
		objectives_to_fetch = ACCOUNT_OBJECTIVES_ALL + OBJECTIVES_MAPS_ALL + OBJECTIVES_CLASSES_ALL\
							 + OBJECTIVES_WEAPONS_ALL

		# When updating player data, account_ids is a triple (account_id, user_id, username)
		# account_id - firesky account id, user_id - website account user id
		# username - website account username
		if not self.account_ids:
			return
		
		date = datetime.datetime.now()
		today = date.date()
		date_value = "%s-%s-%s" % (today.year, today.month, today.day)

		players_objectives = []
		for account_id, user_id, username in self.account_ids:
			account_id = int(account_id)
			user_id = int(user_id)
			player_objectives = self.fetch_player_objective_list(account_id)
			
			if not player_objectives:
				continue
			
			dom = minidom.parseString(player_objectives)
			
			# Loop over all the available objectives
			empty_count = 0
			player_data = {'account_id': account_id, 'user_id': user_id,
							'username': username, 'date_short': date_value,
							'date_full': date, 'data': {}}
			player_objectives = player_data['data']
			for node in dom.getElementsByTagNameNS(OBJECTIVE_LIST_NS, 'Objective'):
				objective_id = node.getAttribute('ObjectiveID')
				objective_value = node.getAttribute('ProgressValue')
				
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
				continue
			
			# Calculate K/D and hit ratio
			types = ['Account']
			for type in types:
				try:
					player_objectives['%s_%s_%s' % ('SGR', type, 'KillDeathRatio')] = float(player_objectives['%s_%s_%s' % ('SGR', type, 'KillsTotal')]) / float(player_objectives['%s_%s_%s' % ('SGR', type, 'KilledTotal')])
					player_objectives['%s_%s_%s' % ('SGR', type, 'HitRatio')] = (float(player_objectives['%s_%s_%s' % ('SGR', type, 'ShotsHit')]) / float(player_objectives['%s_%s_%s' % ('SGR', type, 'ShotsFired')])) * 100
				except ZeroDivisionError:
					player_objectives['%s_%s_%s' % ('SGR', type, 'KillDeathRatio')] = 0
					player_objectives['%s_%s_%s' % ('SGR', type, 'HitRatio')] = 0
			
			database.rankings_data.save(player_data)

def update_players_data(action = 'update_both'):
	if action == 'update_rankings_data':
		player_ids = list(set(UserProfile.objects.filter(Q(account_id__isnull = False)) \
							  .values_list('account_id', 'user__id', 'user__username')))
	else:
		player_ids = database.players_objective_lists.distinct('_id')
	
	if not player_ids:
		return
	
	player_ids_count = len(player_ids)
	
	# Multiple threads needed
	if player_ids_count > 2 * MAX_THREADS:
		items_per_thread = player_ids_count / MAX_THREADS
		chunks = [player_ids[i:items_per_thread + i] for i in range(0, player_ids_count, items_per_thread)]
	else:
		chunks = [player_ids]
	
	threads = []
	for chunk in chunks:
		if action == 'update_objectives' or action == 'update_both':
			threads.append(PlayerUtils(chunk, 'update_objectives'))
		
		if action == 'update_achievements' or action == 'update_both':
			threads.append(PlayerUtils(chunk, 'update_achievements'))
			
		if action == 'update_rankings_data':
			threads.append(PlayerUtils(chunk, 'update_rankings_data'))
			
	# Start the waiting threads
	for thread in threads:
		thread.start()
	
	# Wait for all threads to finish		
	for thread in threading.enumerate():
		if thread is not threading.currentThread():
			thread.join()
	
def ip_to_location(ip_address):
	""" Return IP address origin country, country iso code and city. """
	
	request = urllib2.Request('%s%s' % (IP_TO_COUNTRY_URL, ip_address))
	
	try:
		response = urllib2.urlopen(request, timeout = 8)
	except Exception:
		return None
	else:
		response = response.read()

	try:
		country = response.split('\n')[0].split('Country: ')[1].split(' (')[0].lower()
		country = ' ' . join([token.capitalize() for token in country.split(' ')])
		country_code = response.split('\n')[0].split('(')[1].split(')')[0].lower()
		city = response.split('\n')[1].split('City: ')[1]
	except:
		country = None
		city = None
		country_code = None

	return (country, country_code, city)