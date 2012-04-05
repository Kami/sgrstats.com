from django_assets import Bundle, register

## CSS ##
css_partners_bundle = Bundle('site_media/css/partners.css')
register('css_partners',
		css_partners_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.partners.css')

## Javascript ##