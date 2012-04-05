import datetime

from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.http import HttpResponse, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.utils.cache import _generate_cache_header_key, get_cache_key
from django.core.cache import cache

from mongodb import *

from sgrstats.static import *
from stats.views import _get_cache_key_name
from stats.models import UserProfile

from core.views import update_online_users

@update_online_users
def top_player(request):
	players = get_top_players()
	date_updated = players[0]['date_full']
	
	return render_to_response('rankings/top_player.html', {'players': players, 'date_updated': date_updated}, \
							  context_instance = RequestContext(request))

@update_online_users  
def top_class(request):
	classes = get_top_classes()
	date_updated = get_top_players()[0]['date_full']
	
	return render_to_response('rankings/top_class.html', {'classes': classes, 'date_updated': date_updated}, \
							  context_instance = RequestContext(request))

@update_online_users   
def top_map(request):
	maps = get_top_maps()
	date_updated = get_top_players()[0]['date_full']
	
	return render_to_response('rankings/top_map.html', {'maps': maps, 'date_updated': date_updated}, \
							  context_instance = RequestContext(request))

@update_online_users
def top_weapon(request):
	weapons = get_top_weapons()
	date_updated = get_top_players()[0]['date_full']
	
	return render_to_response('rankings/top_weapon.html', {'weapons': weapons, 'date_updated': date_updated}, \
							  context_instance = RequestContext(request))
	
# Helper functions
def get_top_players():
	""" Retrieves players with a linked account from the database. """
	key = _get_cache_key_name('player.rankings', 'top_players')
	players = cache.get(key, False)
	
	if players != False:
		return players

	# Players not in cache, retrieve from MongoDB append to list and save in memcache
	today = datetime.datetime.now().date()
	date = "%s-%s-%s" % (today.year, today.month, today.day)
	players_cursor = database.rankings_data.find({'date_short': date}) \
					.sort('data.SGR_Account_ExperiencePointsEarned', -1)
	
	# Players which don't want to be shown on the rankings page
	players_hidden = UserProfile.objects.filter(show_on_rankings = False) \
					.values_list('account_id', 'user__id')
	
	players = []
	for index, player in enumerate(players_cursor):
		player['data'] = format_total_played_times(player['data'])
		player['rank'] = index + 1
		
		account_id = int(player['account_id'])
		user_id = player['user_id']
		
		if (account_id, user_id) in players_hidden:
			player['hide'] = True
		else:
			player['hide'] = False
			
		player['rank'] = index + 1
		players.append(player)

	cache.set(key, players, 10 * 60)
	return players

def get_top_classes():
	""" Retrieves top classes data from the database. """
	cache_key = _get_cache_key_name('player.rankings', 'top_classes')
	top_classes = cache.get(cache_key, False)
	
	if top_classes != False:
		return top_classes
	
	date = datetime.datetime.now()
	today = date.date()
	date_value = "%s-%s-%s" % (today.year, today.month, today.day)
	
	result = database.top_classes.find({'_id': date_value}).limit(1)[0]
	top_classes_data = result['data']
	
	top_classes = {}
	keys = top_classes_data.keys()
	for player_class in AVAILABLE_CLASSES:
		# Result keys belonging to this class
		class_keys = [key for key in keys if key.find(player_class) != -1]
		
		# Values belonging to this class
		class_values = {}
		for key in class_keys:
			# Parse the actual objective from the key name
			# SGR_Ashrak_DamageDealtTotal -> DamageDealtTotal
			objective = key.replace('SGR_%s_' % (player_class), '')
			class_values[objective] = int(top_classes_data[key])
		
		class_values = format_total_played_times(class_values)
		top_classes[player_class] = class_values

	cache.set(cache_key, top_classes, 3 * 60 * 60)
	return top_classes

def get_top_maps():
	""" Retrieves top maps data from the database. """
	cache_key = _get_cache_key_name('player.rankings', 'top_maps')
	top_maps = cache.get(cache_key, False)
	
	if top_maps != False:
		return top_maps

	date = datetime.datetime.now()
	today = date.date()
	date_value = "%s-%s-%s" % (today.year, today.month, today.day)
	
	result = database.top_maps.find({'_id': date_value}).limit(1)[0]
	top_maps_data = result['data']
	
	top_maps = {}
	keys = top_maps_data.keys()
	for map in AVAILABLE_MAPS:
		# Result keys belonging to this class
		map_keys = [key for key in keys if key.find(map) != -1]
		
		# Values belonging to this map
		map_values = {}
		for key in map_keys:
			# Parse the actual objective from the key name
			# SGR_Account_TimePlayedOnAmarna -> TimePlayed
			objective = key.replace('SGR_Account_', '').replace('On%s' % (map), '')
			
			try:
				map_values[objective] = int(top_maps_data[key])
			except:
				map_values[objective] = 0
		
		map_values = format_total_played_times(map_values)
		top_maps[map] = map_values
	
	cache.set(cache_key, top_maps, 3 * 60 * 60)
	return top_maps

def get_top_weapons():
	""" Retrieves top weapons data from the database. """
	cache_key = _get_cache_key_name('player.rankings', 'top_weapons')
	top_weapons = cache.get(cache_key, False)
	
	if top_weapons != False:
		return top_weapons

	date = datetime.datetime.now()
	today = date.date()
	date_value = "%s-%s-%s" % (today.year, today.month, today.day)
	
	result = database.top_weapons.find({'_id': date_value}).limit(1)[0]
	top_weapons_data = result['data']
	
	top_weapons = {}
	keys = top_weapons_data.keys()
	for weapon in AVAILABLE_WEAPONS:
		# Result keys belonging to this class
		weapon_keys = [key for key in keys if key.find(weapon) != -1]
		
		# Values belonging to this map
		weapon_values = {}
		for key in weapon_keys:
			# Parse the actual objective from the key name
			# SGR_DesertEagle_Headshots -> Headshots
			objective = key.replace('SGR_Account_', '') \
						   .replace('With', '') \
						   .replace('By', '') \
						   .replace('Using', '') \
						   .replace('%s' % (weapon), '')
			weapon_values[objective] = int(top_weapons_data[key])
		
		weapon_values = format_total_played_times(weapon_values)
		top_weapons[weapon] = weapon_values
	
	cache.set(cache_key, top_weapons, 3 * 60 * 60)
	return top_weapons

def format_total_played_times(objectives):
	""" Formats played times from seconds to <hh>h <mm>min. """
	
	for objective_id in objectives.keys():
		# Format total played time
		if objective_id.find('TimePlayed') != -1:
			time_played = objectives[objective_id]
			hours = time_played / 60 / 60
			minutes = (time_played - (hours * 60 * 60)) / 60
			
			objectives['%sFormatted' % (objective_id)] = '%sh %smin' % (hours, minutes)
			 
	return objectives				 