from piston.handler import BaseHandler
from piston.utils import throttle

from sgrstats.stats.views import get_player_objectives, get_player_achievements

#@todo: response caching for each account for 60 minutes
class PlayerObjectivesHandler(BaseHandler):
    """ 
    Get player objectives for specified account id.
    """
    
    allowed_methods = ('GET', )
    field_mappings = {
            'experience_points': 'SGR_Account_ExperiencePointsEarned',
            'kills': 'SGR_Account_KillsTotal',
            'deaths': 'SGR_Account_KilledTotal',
            'shots_fired': 'SGR_Account_ShotsFired',
            'shots_hit': 'SGR_Account_ShotsHit',
            'wins_total': 'SGR_Account_WinsTotal',
            'losses_total': 'SGR_Account_LossesTotal',
            'time_played_total': 'SGR_Account_TimePlayedTotal',
            '': 'date_retrieved',
    }
    
    @throttle(10, 60 * 60)
    def read(self, request, account_id):
        player_stats = get_player_objectives(account_id, self.field_mappings.values())
        
        response = {}
        player_objectives = {}
        
        # In-existent player
        if not player_stats:
            error_message = {
                'request': request.path,
                'error': 'Player with this account ID was not found.',
            }
            
            return error_message
    
        # Do the field remapping
        response = {'meta': {
                             'account_id': account_id,
                             'date_retrieved': player_stats['date_retrieved']
                    }, 'objectives': {}}  
        
        for key, value in self.field_mappings.iteritems():
            if key != '':
                player_objectives[key] = player_stats[value]

        del player_stats

        response['objectives']['account'] = player_objectives
        
        return response
    
class PlayerAchievementsHandler(BaseHandler):
    """
    Get player achievements for specified account ID.
    """
    
    allowed_methods = ('GET', )
    field_mappings = {
            'id': 'id',
            'title': 'title',
            'category': 'category',
            'points': 'points',
            'completed_on': 'completed_on',
    }
    
    @throttle(10, 60 * 60)
    def read(self, request, account_id):
        player_stats = get_player_achievements(account_id)

        response = {}
        player_achievement = {}
        
        # In-existent player
        if not player_stats:
            error_message = {
                'request': request.path,
                'error': 'Player with this account ID was not found.',
            }
            
            return error_message
    
        # Do the field remapping
        response = {'meta': {
                             'account_id': account_id,
                             'date_retrieved': player_stats['date_retrieved']
                    }, 'achievements': []}  

        for index, achievement in enumerate(player_stats['achievements']):
            for key, value in self.field_mappings.iteritems():
                player_achievement[key] = player_stats['achievements'][index][value]
            
            response['achievements'].append(player_achievement)
        
        return response