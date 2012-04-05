from django_assets import Bundle, register

## CSS ##
css_news_bundle = Bundle('site_media/css/news.css')
register('css_news',
		css_news_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.news.css')

## Javascript ##