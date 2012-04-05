from django_assets import Bundle, register

## CSS ##
css_rankings_bundle = Bundle('site_media/css/rankings/navigation.css',
							 'site_media/css/rankings/global.css',
							 'site_media/css/rankings/top_player.css',
							 'site_media/css/table_sorter.css')
register('css_rankings',
		css_rankings_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.rankings.css')

## Javascript ##
js_rankings_bundle = Bundle('site_media/js/jquery.tablesorter.min.js',
							'site_media/js/jquery.tablesorter.pager.js',
							'site_media/js/tablesorter_parsers.js',
							'site_media/js/jquery.columnhover.pack.js',
							'site_media/js/jquery.quicksearch.js')
register('js_rankings',
		js_rankings_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.rankings.js')