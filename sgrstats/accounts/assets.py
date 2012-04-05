from django_assets import Bundle, register
from core.assets import css_base_bundle

## CSS ##
css_accounts_bundle = Bundle('site_media/css/settings.css',
							'site_media/css/boxy.css')
css_accounts_signatures_bundle = Bundle('site_media/css/signature_images.css')
register('css_accounts',
		css_accounts_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.accounts.css')
register('css_accounts_signatures',
		css_base_bundle,
		css_accounts_bundle,
		css_accounts_signatures_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.accounts_signatures.css')

# Registration
css_registration_bundle = Bundle('site_media/css/validationEngine.jquery.css')
register('css_registration',
		css_registration_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.registration.css')

## Javascript ##
js_accounts_bundle = Bundle('site_media/js/jquery.boxy.js')
register('js_accounts',
		js_accounts_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.accounts.js')

# Registration
js_registration_bundle = Bundle('site_media/js/jquery.validationEngine.js',
							'site_media/js/jquery.validationEngine-en.js')
register('js_registration',
		js_registration_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.registration.js')