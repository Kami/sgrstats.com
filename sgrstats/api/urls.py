from django.conf.urls.defaults import *
from piston.resource import Resource

from sgrstats.api.handlers import PlayerObjectivesHandler, PlayerAchievementsHandler

player_objectives_handler = Resource(PlayerObjectivesHandler)
player_achievements_handler = Resource(PlayerAchievementsHandler)

urlpatterns = patterns('',
    # objectives/player_id, achievements/player_id
    url(r'^objectives/(?P<account_id>\d+)\.(?P<emitter_format>.+)', player_objectives_handler),
    url(r'^achievements/(?P<account_id>\d+)\.(?P<emitter_format>.+)', player_achievements_handler),
)
