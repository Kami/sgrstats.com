# General
CLASS_CATEGORIES = (
            (0, 'Stargate Command'),
            (1, 'System Lords')
)

USER_AGENT = 'UE3-SGB'
IP_TO_COUNTRY_URL = 'http://api.hostip.info/get_html.php?ip='

# FireSky API related constants
SERVER_LIST_URL = 'http://ws.firesky.com/SGBLogin/ServerListAll'
OBJECTIVE_LIST_URL = 'http://rep1.firesky.com/RegistrationWS/AccountObjectiveGet'
ACHIEVEMENT_LIST_URL = 'http://rep1.firesky.com/RegistrationWS/AccountAchievementGet'

OBJECTIVE_LIST_NS = 'http://www.cheyenneme.com/xml/registration'
ACHIEVEMENT_LIST_NS = 'http://www.cheyenneme.com/xml/registration'

# Rankings related variables
ACCOUNT_OBJECTIVES_ALL = ['SGR_Account_TimePlayedTotal', 'SGR_Account_Headshots',
                          'SGR_Account_ExperiencePointsEarned', 'SGR_Account_HighestMatchKillStreak',
                          'SGR_Account_KillsTotal', 'SGR_Account_KilledTotal',
                          'SGR_Account_WinsTotal', 'SGR_Account_LossesTotal',
                          'SGR_Account_ShotsFired', 'SGR_Account_ShotsHit',
                          'SGR_Account_DamageDealtTotal', 'SGR_Account_HealingGivenByHandDevice',
                          'SGR_Account_HealingGivenByHaraKesh', 'SGR_Account_HealingGivenByHypoDispenser',
                          'SGR_Account_HealingGivenByHypoSpray', 'SGR_Account_HealingGivenTotal',
                          'SGR_Account_HealingReceivedTotal']

# Leonops - Court = TDM game type, Arena = Arena game type
AVAILABLE_MAPS = ('Amarna', 'SGC', 'Whiteout', 'Court', 'Arena')
OBJECTIVES_MAPS = ('SGR_Account_WinsOn%s',
                   'SGR_Account_LossesOn%s', 'SGR_Account_TimePlayedOn%s')
OBJECTIVES_MAPS_ALL = [(objective % map) for objective in OBJECTIVES_MAPS for map in AVAILABLE_MAPS]

AVAILABLE_CLASSES = ('Soldier', 'Commando', 'Scientist', 'Goauld', 'Jaffa', 'Ashrak')
OBJECTIVES_CLASSES = ('SGR_%s_KillsTotal', 'SGR_%s_KilledTotal', 'SGR_%s_DamageDealtTotal',
                      'SGR_%s_Headshots', 'SGR_%s_TimePlayedTotal')
OBJECTIVES_CLASSES_ALL = [(objective % player_class) for objective in OBJECTIVES_CLASSES for player_class in AVAILABLE_CLASSES]


AVAILABLE_WEAPONS = ('AshrakBlade', 'Beretta', 'Claymore', 'DesertEagle', 'DiseaseCloud',
                     'GrenadeLauncher', 'HandDevicePush', 'HandDeviceZap', 'P90', 'SniperRifle',
                     'StaffBlast', 'StaffMelee', 'Turret')
OBJECTIVES_WEAPONS = ('SGR_Account_KillsUsing%s', 'SGR_Account_DamageDealtWith%s', 'SGR_Account_DamageTakenBy%s')
OBJECTIVES_WEAPONS_ALL = [(objective % weapon) for objective in OBJECTIVES_WEAPONS for weapon in AVAILABLE_WEAPONS]