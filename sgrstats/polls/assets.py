from django_assets import Bundle, register

## CSS ##
css_poll_bundle = Bundle('site_media/css/poll.css')
register('css_poll',
		css_poll_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.poll.css')

## Javascript ##