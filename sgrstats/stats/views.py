# Python
import operator
import datetime
import random
import time

# Django
from django.shortcuts import render_to_response, get_object_or_404, HttpResponse, HttpResponseRedirect, Http404
from django.http import HttpResponse, Http404
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from mongodb import *
from utils import PlayerUtils

from django.utils.cache import _generate_cache_header_key, get_cache_key
from django.core.cache import cache

# Other
from pyofc2 import * 
from stats.utils import ServerListUtils, PlayerUtils
from stats.models import UserProfile, ClassRank

from core import bitly
from core.views import update_online_users

@update_online_users
def index(request):
	try:
		member_id = request.POST['member_id']
		
		if not member_id:
			return render_to_response('stats/index.html', context_instance = RequestContext(request)) 
		
		try:
			member_id = int(member_id)
		except ValueError:
			return render_to_response('stats/index.html', context_instance = RequestContext(request)) 
		
		return HttpResponseRedirect(reverse('stats_summary', args = (member_id,)))
	except KeyError:
		# No member ID is provided
		if request.user.is_authenticated() and request.user.get_profile().account_id:
			# Member with a linked account, redirect him to the page with his stats
			return HttpResponseRedirect(reverse('stats_summary', args = (int(request.user.get_profile().account_id),)))
			
		return render_to_response('stats/index.html', context_instance = RequestContext(request))

@update_online_users
def servers(request):
	server_list = get_server_list()
	date_retrieved = server_list[0]['date_retrieved']
	player_count = sum([server['sgc_player_count'] + server['sl_player_count'] for server in server_list])
	player_count_max = len(server_list) * 16
	
	return render_to_response('stats/servers.html', {'servers': server_list, 'date_retrieved': date_retrieved, 'player_count': player_count, 'player_count_max': player_count_max}, context_instance = RequestContext(request))

@update_online_users
def stats(request, account_id, what):
	if what not in ['summary', 'kills', 'classes', 'maps', 'achievements']:
		raise Http404()

	url = reverse('stats_%s_data' % (what), args = (account_id,))
	return render_to_response('stats/loading.html', {'account_id': account_id, 'username': get_player_username(account_id), 'what': what, 'url': url}, context_instance = RequestContext(request))

def summary(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	
	if not player_stats:
		return error_page(request, account_id, error_type = 2 if player_stats == False else 1)
	
	player_achievements = get_player_achievements(request, account_id)

	if not player_achievements:
		return error_page(request, account_id, error_type = 2 if player_achievements == False else 1)
	
	latest_achievements = get_player_latest_completed_achievements(player_achievements)[:6]

	top_class = get_player_top_class_by_kills(player_stats)
	top_class_image = random.sample(['jaffa', 'jaffa_sobek'], 1)[0] if top_class == 'jaffa' else top_class
	top_class_data = get_player_top_class_data(player_stats, top_class)
	top_map = get_player_top_map_by_wins(player_stats)
	worst_map = get_player_worst_map_by_loses(player_stats)
	rival_class = get_player_rival_class(player_stats)
	easy_class = get_player_easy_class(player_stats)
	
	# Logged-in user is viewing its own stats
	if request.user.is_authenticated() and request.user.get_profile().account_id:
		account_id_linked = request.user.get_profile().account_id

		if int(account_id) == account_id_linked:
			current_site = Site.objects.get_current()
			current_site_url = current_site.domain
			api = bitly.Api(login = 'sgrstats', apikey = 'R_88fd4a0cace4cbf92c1cd588531694c3')
			
			try:
				bitly_url = api.shorten('%s%s' % (current_site_url, reverse('stats_summary', args = (account_id,))))
			except:
				bitly_url = None
		else:
			bitly_url = None
	else:
		bitly_url = None
	
	return render_to_response('stats/summary.html', {
													 'account_id': int(account_id),
													 'username': get_player_username(account_id),
													 'bitly_url': bitly_url,
													 'player_stats': player_stats,
													 'top_class': top_class,
													 'top_class_image': top_class_image,
													 'top_class_data': top_class_data,
													 'latest_achievements': latest_achievements,
													 'top_map': top_map,
													 'worst_map': worst_map,
													 'rival_class': rival_class,
													 'easy_class': easy_class}, context_instance = RequestContext(request))

def kills(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	
	if not player_stats:
		return error_page(request, account_id, error_type = 2 if player_stats == False else 1)
	
	return render_to_response('stats/kills.html', {'account_id': int(account_id), 'username': get_player_username(account_id), 'player_stats': player_stats}, context_instance = RequestContext(request))

def classes(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	
	if player_stats is None:
		return error_page(request, account_id, error_type = 1)
	elif player_stats is False:
		return error_page(request, account_id, error_type = 2)
	
	return render_to_response('stats/classes.html', {'account_id': int(account_id), 'username': get_player_username(account_id), 'player_stats': player_stats}, context_instance = RequestContext(request))

def maps(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	
	if not player_stats:
		return error_page(request, account_id, error_type = 2 if player_stats == False else 1)
	
	top_class = get_player_top_class_by_map(player_stats)
	worst_class = get_player_worst_class_by_map(player_stats)
	
	return render_to_response('stats/maps.html', {'account_id': int(account_id), 'username': get_player_username(account_id), 'player_stats': player_stats, 'top_class': top_class, 'worst_class': worst_class}, context_instance = RequestContext(request))

def achievements(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	player_achievements = get_player_achievements(request, account_id)
	
	if not player_stats or not player_achievements:
		return error_page(request, account_id, error_type = 2 if player_stats == False else 1)
	
	player_completed_achievements = get_player_completed_achievements(player_achievements)
	
	try:
		total_count = player_achievements['total_count']
		completed_count = player_achievements['completed_count']
	except KeyError:
		total_count = 0
		completed_count = 0
	
	if total_count and completed_count:
		percent_completed = (float(completed_count) / float(total_count)) * 100
	else:
		percent_completed = 0
	
	if not player_completed_achievements:
		return error_page(request, account_id, error_type = 3)

	return render_to_response('stats/achievements.html', {'account_id': int(account_id), 'username': get_player_username(account_id), 'player_stats': player_stats, 'player_achievements': player_completed_achievements, 'total_count': int(total_count), 'completed_count': int(completed_count), 'percent_completed': percent_completed}, context_instance = RequestContext(request))

# @todo: To implement.
def leaderboards(request, account_id):
	player_stats = get_player_objectives(request, account_id)
	
	if player_stats is None:
		return error_page(request, account_id, error_type = 1)
	elif player_stats is False:
		return error_page(request, account_id, error_type = 2)
	
	return render_to_response('stats/leaderboards.html', {'account_id': int(account_id), 'player_stats': player_stats}, context_instance = RequestContext(request))

# Helper functions
def get_server_list():
	server_list = database.servers.find().sort('sgc_player_count', -1)
	
	if server_list.count() == 0:
		# No data about servers is available
		server_utils = ServerListUtils()
		server_list = server_utils.update_server_list(return_fetched_data = True)
		
	server_list = format_total_player_count(server_list)
		
	return server_list
		
def get_player_objectives(request, account_id, fields = None):
	key = _get_cache_key_name('player.objectives', account_id)
	player_stats = cache.get(key, False)
	
	if player_stats != False:
		return player_stats
	
	account_id = int(account_id)
	diff = datetime.datetime.now() - datetime.timedelta(seconds = settings.DATA_CACHE_PERIOD)
	player_stats = database.players_objective_lists.find_one({'_id': account_id, 'date_retrieved': {'$gte': diff}}, fields = fields)

	if not player_stats:
		# No data about this player or the data is stale - try to fetch fresh data
		player_utils = PlayerUtils([account_id])
		player_stats = player_utils.update_players_objective_lists(return_fetched_data = True)

		if player_stats == False:
			# FireSky servers are probably offline, retrieve last saved objectives (if any) we have for this user
			player_stats = database.players_objective_lists.find_one({'_id': account_id}, fields = fields)
			
			if not player_stats:
				player_stats = None

	# Format total played times
	if player_stats:
		player_stats = format_classes_rank(format_total_played_times(player_stats))
	
	if player_stats != False:
		# If data was successfully fetched or this player doesn't exist, we cache the value	
		cache.set(key, player_stats, 300)
   
	return player_stats  

def get_player_achievements(request, account_id, fields = None):
	key = _get_cache_key_name('player.achievements', account_id)
	player_achievements = cache.get(key, False)
	
	if player_achievements != False:
		return player_achievements
	
	account_id = int(account_id)
	diff = datetime.datetime.now() - datetime.timedelta(seconds = settings.DATA_CACHE_PERIOD)
	player_achievements = database.players_achievement_lists.find_one({'_id': account_id, 'date_retrieved': {'$gte': diff}}, fields = fields)
	
	if not player_achievements:
		# No data about this player or the data is stale - fetch the fresh data
		player_utils = PlayerUtils([account_id])
		player_achievements = player_utils.update_players_achievement_lists(return_fetched_data = True)
		
		if player_achievements == False:
			# FireSky servers are probably offline retrieve last saved achievements (if any) we have for this user
			player_achievements = database.players_achievement_lists.find_one({'_id': account_id}, fields = fields)
			
			if not player_achievements:
				player_achievements = None
		
	# Format dates
	if player_achievements:
		player_achievements = format_achievements_dates(player_achievements)
		
	if player_achievements != False:
		# If data was successfully fetched or this player doesn't exist, we cache the value
		cache.set(key, player_achievements, 300)
   
	return player_achievements

def get_player_completed_achievements(player_achievements):
	
	completed_achievements = []
	for achievement in player_achievements['achievements']:
		if achievement['completed_on'] != '':
			completed_achievements.append(achievement)
	
	return completed_achievements

def get_player_latest_completed_achievements(player_achievements):
	completed_achievements = get_player_completed_achievements(player_achievements)
	
	achievements = []
	for achievement in completed_achievements:
		achievements.append((achievement['completed_on'], achievement['id'], achievement['title']))
	
	achievements_sorted = sorted(achievements, key = operator.itemgetter(0), reverse = True)
		
	return achievements_sorted

def format_completed_achievements(player_achievements):
	""" Format completed achievements as a dictionary with key = title and value = completed_on. """
	completed_achievements = get_player_completed_achievements(player_achievements)
	achievements = []
	for achievement in completed_achievements:
		achievements.append((achievement['completed_on'], achievement['title']))
		
	return sorted(achievements, key = operator.itemgetter(0))		
	
def get_player_top_class_by_kills(player_stats):
	data = {
		'soldier': player_stats['SGR_Soldier_KillsTotal'],
		'commando': player_stats['SGR_Commando_KillsTotal'],
		'scientist': player_stats['SGR_Scientist_KillsTotal'],
		'goauld': player_stats['SGR_Goauld_KillsTotal'],
		'jaffa': player_stats['SGR_Jaffa_KillsTotal'],
		'ashrak': player_stats['SGR_Ashrak_KillsTotal']
	}
	
	max_value = max(data.values())
	return [k for k,v in data.items() if v == max_value][0]

def get_player_top_map_by_wins(player_stats):
	data = {
		'sgc': player_stats['SGR_Account_WinsOnSGC'],
		'amarna': player_stats['SGR_Account_WinsOnAmarna'],
		'whiteout': player_stats['SGR_Account_WinsOnWhiteout'],
		
		'leonops': (player_stats['SGR_Account_WinsOnCourt'] + player_stats['SGR_Account_WinsOnArena']),
	}
	
	max_value = max(data.values())
	return [(k,v) for k,v in data.items() if v == max_value][0]

def get_player_worst_map_by_loses(player_stats):
	data = {
		'sgc': player_stats['SGR_Account_LossesOnSGC'],
		'amarna': player_stats['SGR_Account_LossesOnAmarna'],
		'whiteout': player_stats['SGR_Account_LossesOnWhiteout'],
		
		'leonops': (player_stats['SGR_Account_LossesOnCourt'] + player_stats['SGR_Account_LossesOnArena']),
	}
	
	max_value = max(data.values())
	return [(k,v) for k,v in data.items() if v == max_value][0]

def get_player_rival_class(player_stats):
	data = {
		'soldier': player_stats['SGR_Account_KilledBySoldier'],
		'commando': player_stats['SGR_Account_KilledByCommando'],
		'scientist': player_stats['SGR_Account_KilledByScientist'],
		'goauld': player_stats['SGR_Account_KilledByGoauld'],
		'jaffa': player_stats['SGR_Account_KilledByJaffa'],
		'ashrak': player_stats['SGR_Account_KilledByAshrak']
	}
	
	max_value = max(data.values())
	return [(k,v) for k,v in data.items() if v == max_value][0]

def get_player_easy_class(player_stats):
	data = {
		'soldier': player_stats['SGR_Account_SoldierKills'],
		'commando': player_stats['SGR_Account_CommandoKills'],
		'scientist': player_stats['SGR_Account_ScientistKills'],
		'goauld': player_stats['SGR_Account_GoauldKills'],
		'jaffa': player_stats['SGR_Account_JaffaKills'],
		'ashrak': player_stats['SGR_Account_AshrakKills']
	}
	
	max_value = max(data.values())
	return [(k,v) for k,v in data.items() if v == max_value][0]

def get_player_top_class_data(player_stats, top_class):
	top_class_formatted = top_class[0].upper() + top_class[1:]
	data = {
		'kills': player_stats['SGR_%s_KillsTotal' % (top_class_formatted)],
		'deaths': player_stats['SGR_%s_KilledTotal' % (top_class_formatted)],
		'streak': player_stats['SGR_%s_HighestMatchKillStreak' % (top_class_formatted)],
		'wins': player_stats['SGR_%s_WinsTotal' % (top_class_formatted)],
		'losses': player_stats['SGR_%s_LossesTotal' % (top_class_formatted)],
	}
	
	return data

def format_total_played_times(player_stats):
	""" Converts total played time from seconds to hours. """
	
	# Account and classes
	for type in ['Account', 'SGC', 'SystemLords', 'Soldier', 'Commando', 'Scientist', 'Goauld', 'Jaffa', 'Ashrak']:
		time_played = player_stats['SGR_%s_TimePlayedTotal' % (type)]
		hours = time_played / 60 / 60
		minutes = (time_played - (hours * 60 * 60)) / 60
		
		player_stats['SGR_%s_TimePlayedTotal' % (type)] = '%sh %smin' % (hours, minutes)
		
	# Maps
	for map in ['SGC', 'Amarna', 'Whiteout', 'Court', 'Arena']:
		time_played = player_stats['SGR_Account_TimePlayedOn%s' % (map)]
		hours = time_played / 60 / 60
		minutes = (time_played - (hours * 60 * 60)) / 60
		
		player_stats['SGR_Account_TimePlayedOn%s' % (map)] = '%sh %smin' % (hours, minutes)
	
	return player_stats

def format_classes_rank(player_stats):
	""" Calculates classes current rank """

	for player_class in [(0, 'Soldier'), (0, 'Commando'), (0, 'Scientist'), (1, 'Goauld'), (1, 'Jaffa'), (1, 'Ashrak')]:
		exp_current =  player_stats['SGR_%s_ExperiencePointsEarned' % (player_class[1])]
		
		try:
			class_rank = ClassRank.objects.filter(category = player_class[0], exp_min__lte = exp_current).order_by('-exp_min')[0]
			rank_title = class_rank.title
		except IndexError:
			rank_title = 'Unknown'
		
		player_stats['SGR_%s_Rank' % (player_class[1])] = rank_title
		
	return player_stats		

def get_player_top_class_by_map(player_stats):
	classes_wins = {}
	classes_top = {}
	for map in ['SGC', 'Amarna', 'Whiteout', 'Court', 'Arena']:
		
		classes_wins[map] = {}
		classes_top[map] = {}
		for player_class in ['Soldier', 'Commando', 'Scientist', 'Goauld', 'Jaffa', 'Ashrak']:
			classes_wins[map][player_class] =  int(player_stats['SGR_%s_WinsOn%s' % (player_class, map)])
			
		max_value = max(classes_wins[map].values())
		classes_top[map] = [(k,v) for k,v in classes_wins[map].items() if v == max_value][0]
			
	return classes_top

def get_player_worst_class_by_map(player_stats):
	classes_losses = {}
	classes_worst = {}
	for map in ['SGC', 'Amarna', 'Whiteout', 'Court', 'Arena']:
		
		classes_losses[map] = {}
		classes_worst[map] = {}
		for player_class in ['Soldier', 'Commando', 'Scientist', 'Goauld', 'Jaffa', 'Ashrak']:
			classes_losses[map][player_class] =  int(player_stats['SGR_%s_LossesOn%s' % (player_class, map)])
			
		max_value = max(classes_losses[map].values())
		classes_worst[map] = [(k,v) for k,v in classes_losses[map].items() if v == max_value][0]
			
	return classes_worst

def format_achievements_dates(player_achievements):
	for achievement in player_achievements['achievements']:
		completed_on = achievement['completed_on']
		
		if completed_on != '':
			achievement['completed_on'] = datetime.datetime.strptime(achievement['completed_on'].split('.000')[0], '%Y-%m-%dT%H:%M:%S')
	
	return player_achievements

def format_total_player_count(server_list):
	servers = []
	for server in server_list:
		server['total_player_count'] = server['sgc_player_count'] + server['sl_player_count']
		servers.append(server)
	
	return servers

def get_next_rank_title_and_exp_points(class_category = 0, exp_current = 0):
	try:
		class_rank = ClassRank.objects.filter(category = class_category, exp_min__gt = exp_current).order_by('exp_min')[0]
	except IndexError:
		return None
		
	title = class_rank.title
	exp_total = class_rank.exp_min
	exp_needed = exp_total - exp_current
	
	return (title, exp_needed, exp_total)

def get_player_username(account_id):
	"""
	Returns player's username if player with this account ID has a linked account,
	None otherwise.
	"""
	key = _get_cache_key_name('player.stats.u', account_id)
	username = cache.get(key, False)
	
	if username != False:
		return username

	try:
		username = UserProfile.objects.get(account_id = account_id).user.username
	except (ObjectDoesNotExist, MultipleObjectsReturned):
		username = None
	
	cache.set(key, username)
	
	return username

# Other
def error_page(request, account_id, error_type = 1):
	return render_to_response('stats/error.html', {'account_id': int(account_id), 'error_type': error_type}, context_instance = RequestContext(request))

def _get_cache_key_name(prefix, account_id):
	return '%s.%s' % (prefix, account_id)