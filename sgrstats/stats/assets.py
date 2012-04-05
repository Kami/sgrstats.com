from django_assets import Bundle, register

## CSS ##
# Stats
css_stats_index_bundle = Bundle('site_media/css/stats/navigation.css',
						  'site_media/css/stats/index.css')
register('css_stats_index',
		css_stats_index_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.stats_index.css')

css_stats_bundle = Bundle('site_media/css/stats/navigation.css',
						  'site_media/css/stats/top_bar.css',
						  'site_media/css/stats/summary.css',
						  'site_media/css/stats/kills.css',
						  'site_media/css/stats/classes.css',
						  'site_media/css/stats/maps.css',
						  'site_media/css/stats/achievements.css')
register('css_stats',
		css_stats_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.stats.css')

css_achievements_bundle = Bundle('site_media/css/stats/navigation.css',
						  'site_media/css/stats/top_bar.css',
						  'site_media/css/stats/achievements.css',
						  'site_media/css/table_sorter.css')
register('css_achievements',
		css_achievements_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.achievements.css')

# Servers
css_servers_bundle = Bundle('site_media/css/stats/servers.css',
						  	'site_media/css/table_sorter.css')
register('css_servers',
		css_servers_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.servers.css')

## Javascript ##
# Stats
js_achievements_bundle = Bundle('site_media/js/jquery.color.js',
								'site_media/js/jquery.highlight.js',
								'site_media/js/jquery.tablesorter.min.js')
register('js_achievements',
		js_achievements_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.achievements.js')

# Servers
js_servers_bundle = Bundle('site_media/js/jquery.tablesorter.min.js')
register('js_servers',
		js_servers_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.servers.js')