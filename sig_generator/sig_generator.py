# -*- coding: utf-8 -*-
#
# Name: Stargate Resistance Dynamic Signature Generator
# Description: Script for generating dynamic signature images for SGR players.
# Author: Tomaž Muraus (http://www.tomaz-muraus.info)
# Version: 1.3.0

import os
import sys
import fcntl
import stat
import hashlib
import datetime
import threading
import optparse
import ConfigParser
import Image, ImageDraw, ImageFont

root_path = os.path.abspath(os.path.dirname(__file__) + '/../')
sys.path.insert(0, os.path.join(root_path, 'sgrstats'))
sys.path.insert(0, root_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sgrstats.settings'

from django.db.models import Q
from sgrstats.stats.models import UserProfile
from mongodb import connection, database

from sgrstats.settings import SIGNATURE_DATA_STALE_THRESHOLD
from sgrstats.settings import SIGNATURE_GENERATE_INTERVAL
from sgrstats.stats.utils import PlayerUtils

config = ConfigParser.ConfigParser()

PID_FILE = '/tmp/sig_generator.pid'

class PlayerStats(object):
    def __init__(self, member_id, experience, time_played, kills, deaths, suicides, kd_ratio, hit_ratio):
        self.member_id = member_id
        self.experience = experience
        self.time_played = self.format_time_played(time_played)
        self.kills = kills
        self.deaths = deaths
        self.suicides = suicides
        self.kd_ratio = '%.2f' % (kd_ratio)
        self.hit_ratio = '%.2f%%' % (hit_ratio)
        
    def get_hash(self):
        """ Return stats hash which is saved and later used for checking if user stats has changed. """
        hash = hashlib.md5('%s.%s.%s.%s.%s.%s.%s.%s' % (self.member_id, self.experience, self.time_played, self.kills, self.deaths, self.suicides, self.kd_ratio, self.hit_ratio)).hexdigest()
        
        return hash
        
    def format_time_played(self, time_played):
        """ Returns time played in hours. """
        hours = int(time_played / 60.0 / 60)
        minutes = int((time_played - (hours * 60 * 60)) / 60.0)
        
        return ('%sh %sm' % (hours, minutes))
        
class SignatureGenerator(threading.Thread):
    def __init__(self, player_stats_objects = None):
        self.template_path = config.get('general', 'template_path')
        self.output_path = config.get('general', 'output_path')
        self.font_path = config.get('general', 'font_path')
        
        self.templates = [os.path.join(config.get('general', 'template_path'), template) for template in os.listdir(config.get('general', 'template_path')) if os.path.splitext(template)[1] != '.ini']

        """# Load default template meta data
        if not config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'defaults.ini')):
            raise Exception('Missing config file for the default template values')
            
        self.template_default_meta = {}
        texts = dict([(item[0], item[1]) for item in config.items('texts')])
        offsets = dict([(item[0], (item[1].split('|'))) for item in config.items('text_offsets')])
        font_faces = dict([(item[0], item[1]) for item in config.items('font_faces')])
        font_colors = dict([(item[0], item[1]) for item in config.items('font_colors')])
        font_sizes = dict([(item[0], item[1]) for item in config.items('font_sizes')])
            
        self.templates_default_meta = {'texts': texts, 'offsets': offsets, 'font_faces': font_faces, 'font_colors': font_colors, 'font_sizes': font_sizes}"""

        # Load each template setting into a dictionary
        self.templates_meta = {}
        for template in self.templates:
            template_name = os.path.basename(template)
            template_config = os.path.splitext(template)[0] + '.ini'
            
            # Update the dictionary with the default settings
            self.templates_meta[template_name] = {}
            #self.templates_meta[template_name] = self.templates_default_meta
            config_template = ConfigParser.ConfigParser()
            if not config_template.read(template_config):
                continue

            texts = dict([(item[0], item[1]) for item in config_template.items('texts')])
            offsets = dict([(item[0], (item[1].split('|'))) for item in config_template.items('text_offsets')])
            font_faces = dict([(item[0], item[1]) for item in config_template.items('font_faces')])
            font_colors = dict([(item[0], item[1]) for item in config_template.items('font_colors')])
            font_sizes = dict([(item[0], item[1]) for item in config_template.items('font_sizes')])
            
            self.templates_meta.update({template_name: {'texts': texts, 'offsets': offsets, 'font_faces': font_faces, 'font_colors': font_colors, 'font_sizes': font_sizes}})
            self.clear_template_config_file(config_template)
            
        self.player_stats_objects = player_stats_objects
        threading.Thread.__init__(self)
    
    def run(self):
        if self.player_stats_objects is None:
            return
        
        player_count = len(self.player_stats_objects)
        for template in self.templates:
            
            template_name = os.path.basename(template)         
            # Generate signature image for every player
            for player in self.player_stats_objects:
                img = Image.open(template)
                draw = ImageDraw.Draw(img)
                
                output_directory = os.path.join(self.output_path, os.path.split(template)[1].split('.')[0])
                if not os.path.exists(output_directory):
                    # If the output directory doesn't yet exists, we create it
                    os.mkdir(output_directory)
                
                (file_name, file_extenstion) = os.path.splitext(template_name)
                output_path = os.path.join(output_directory, '%s%s' % (player.member_id, file_extenstion))

                # Add all the text items to the image
                for key, value in self.templates_meta[template_name]['texts'].items():
                    font = ImageFont.truetype(os.path.join(self.font_path, self.templates_meta[template_name]['font_faces'][key]), int(self.templates_meta[template_name]['font_sizes'][key]))
                    if key.startswith('__'):
                        # Keys starting with double underscore are considered as special "text only" keys
                        text = value
                    elif key.startswith('_'):
                        # Keys starting with single underscore are considered as special "value only" keys
                        text = str(getattr(player, key[1:]))
                    else:
                        text = '%s %s' % (value, str(getattr(player, key)))
                        
                    (text_width, text_height) = draw.textsize(text, font = font)

                    (offset_x, offset_y) = self.calculate_text_offset(int(self.templates_meta[template_name]['offsets'][key][0]), int(self.templates_meta[template_name]['offsets'][key][1]), text_width, text_height)
                    draw.text((offset_x, offset_y), text, font = font, fill = self.templates_meta[template_name]['font_colors'][key])

                del draw
                output_format = 'JPEG' if file_extenstion == '.jpg' else 'PNG'
                
                img.save(output_path, output_format, quality = 100)
                os.chmod(output_path, stat.S_IREAD | stat.S_IWRITE | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                del img 
    
    def clear_template_config_file(self, config_template):
        """ Clears the config file buffer. """
        config_template.remove_section('texts')
        config_template.remove_section('text_offsets')
        config_template.remove_section('font_faces')
        config_template.remove_section('font_sizes')
        config_template.remove_section('font_colors')
    
    def get_header_position_x(self):
        (header_width, header_height) = draw.textsize(self.text_dict['header'][0], font = ImageFont.truetype(self.font_path, self.text_dict['header'][1]))
        return ((config.get('settings', 'img_with') / 2) - (header_width / 2), 8)
    
    def calculate_text_offset(self, initial_offset_x, initial_offset_y, text_width, text_height):
        """ Calculates the text offset based on the text width and height (initial supplied offsets are center positions). """
        offset_x = initial_offset_x - (text_width / 2.0)
        offset_y = initial_offset_y - (text_height / 2.0)
        
        return (offset_x, offset_y)

def get_players_stats(account_ids, force = False):
    # We only need to update objectives for players whos stats has not been in updated in last 30 minutes
    diff = datetime.datetime.now() - datetime.timedelta(seconds = SIGNATURE_DATA_STALE_THRESHOLD)
    account_ids_fresh = database.players_objective_lists.find({'_id': { '$in': list(account_ids) }, 'date_retrieved': {'$gte': diff}}).distinct('account_id')
    account_ids_to_update = list(set(account_ids) - set(account_ids_fresh))

    # Update players objective list before generating the signature images
    if account_ids_to_update:
        player_utils = PlayerUtils(account_ids_to_update)
        player_utils.update_players_objective_lists()

    player_stats_objects = []
    for account_id in account_ids:
        try:
            player_stat = database.players_objective_lists.find_one({'_id': account_id}, fields = ['account_id', 'SGR_Account_ExperiencePointsEarned', 'SGR_Account_TimePlayedTotal', 'SGR_Account_KillsTotal', 'SGR_Account_KilledTotal', 'SGR_Account_Suicides', 'SGR_Account_KillDeathRatio', 'SGR_Account_HitRatio'])
        except IndexError:
            continue
        
        if not player_stat:
            continue
        
        player_stats = PlayerStats(player_stat['_id'], player_stat['SGR_Account_ExperiencePointsEarned'], player_stat['SGR_Account_TimePlayedTotal'], player_stat['SGR_Account_KillsTotal'], player_stat['SGR_Account_KilledTotal'], player_stat['SGR_Account_Suicides'], player_stat['SGR_Account_KillDeathRatio'], player_stat['SGR_Account_HitRatio'])
        player_stats_hash = player_stats.get_hash()
        
        result = database.players_signature_images_hashes.find_one({'_id': account_id, 'hash': player_stats_hash})
        
        if result and not force:
            # Same hash already exists in the database, sig does not need to be regenerated since
            # the stats has not changed
            continue
        
        # Update the player stats hash
        database.players_signature_images_hashes.save({'_id': account_id, 'hash': player_stats_hash})
        player_stats_objects.append(player_stats)

    return player_stats_objects
        
def generate_signatures(account_ids = None, force = False):
    MAX_THREADS = 8
    
    # Load global settings
    if not config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.ini')):
        raise Exception('Could not read the config file')

    if not account_ids:
        # No account IDs specified, we generate signatures for every user which has signature generation enabled
        # and has had last the signature was checked and possibly generated more then SIGNATURE_GENERATE_INTERVAL seconds ago
        diff = datetime.datetime.now() - datetime.timedelta(seconds = SIGNATURE_GENERATE_INTERVAL)
        
        if force:
            account_ids = set(UserProfile.objects.filter(Q(account_id__isnull = False, dynamic_signature = True)).values_list('account_id', flat = True))
        else:
            account_ids = set(UserProfile.objects.filter(Q(account_id__isnull = False, dynamic_signature = True, date_signature_last_checked__lte = diff) | Q(account_id__isnull = False, dynamic_signature = True, date_signature_last_checked = None)).values_list('account_id', flat = True))

    players = get_players_stats(account_ids, force)
    stats_objects_count = len(players)
    
    if stats_objects_count > MAX_THREADS:
        # Multiple threads needed 
        items_per_thread = stats_objects_count / MAX_THREADS
        chunks = [players[i:items_per_thread + i] for i in range(0, stats_objects_count, items_per_thread)]
    
        for chunk in chunks:
            thread = SignatureGenerator(chunk)
            thread.start()
    else:
        thread = SignatureGenerator(players)
        thread.start()
    
    # Wait for all threads to finish        
    for thread in threading.enumerate():
        if thread is not threading.currentThread():
            thread.join()
    
    # Signature generated date is only updated for those users which stats has changed and new images have been created
    # and the signature last checked update is updated for every player which stats was checked
    updated_account_ids = [player_stats.member_id for player_stats in players]
    update_users_signature_generation_date(updated_account_ids)
    update_users_signature_checked_date(account_ids)
    
def update_users_signature_generation_date(account_ids):
    """ Update last signature generation date for users whom signatures has been generated. """

    UserProfile.objects.filter(account_id__in = account_ids).update(date_signature_generated = datetime.datetime.now())
    
def update_users_signature_checked_date(account_ids):
    """ Update last signature checked date for users whom stats has been checked. """

    UserProfile.objects.filter(account_id__in = account_ids).update(date_signature_last_checked = datetime.datetime.now())

if __name__ == '__main__':
    # Only one instance is allowed to run at once
    fp = open(PID_FILE, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print 'another instance is already running'
        sys.exit(0)

    parser = optparse.OptionParser()
    parser.add_option('-f', '--force', action = 'store_true', default = False, dest = 'force', help = 'force signature generation for all players with signature generation enabled')
    
    (options, args) = parser.parse_args()
    options = vars(options)

    generate_signatures(force = options['force'])
