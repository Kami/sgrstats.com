from django_assets import Bundle, register

## CSS ##
# Base
css_base_bundle = Bundle('site_media/css/style.css',
						 'site_media/css/navigation.css',
						filters = 'yui_css', output = 'site_media/css/gen/packed.base.css')
register('css_base', css_base_bundle)

css_ie_fixes_bundle = Bundle('site_media/css/ie_fixes.css')
register('css_ie_fixes',
		css_ie_fixes_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.ie_fixes.css')

# Index
css_index_bundle = Bundle('site_media/css/index.css')
register('css_index',
		css_index_bundle,
		filters = 'yui_css', output = 'site_media/css/gen/packed.index.css')

## Javascript ##
# Jquery
js_jquery_bundle = Bundle('site_media/js/jquery-1.4.1.min.js',
						  'site_media/js/jquery.qtip-1.0.0-rc3.min.js',
						  'site_media/js/tooltips.js',
						  'site_media/js/hide_message.js')
register('js_jquery',
		js_jquery_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.jquery.js')

# IE6 reject
js_ie6_reject_bundle = Bundle('site_media/js/jquery.reject.min.js',
						  	  'site_media/js/ie6_reject.js')
register('js_ie6_reject',
		js_ie6_reject_bundle,
		output = 'site_media/js/gen/packed.ie6_reject.js')

# Index
js_index_bundle = Bundle('site_media/js/tooltip_deals.js')
register('js_index',
		js_index_bundle,
		filters = 'yui_js', output = 'site_media/js/gen/packed.index.js')