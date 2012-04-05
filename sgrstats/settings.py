# -*- coding: utf-8 -*-
# Django settings for sgrstats project.
import os
import sys
import pymongo
import markdown

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ''),
)

# Debug toolbar
INTERNAL_IPS = ('127.0.0.1', 'localhost')
INTERCEPT_REDIRECTS = False

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sgrstats_sgrstats',
        'USER': 'sgrstats',                  
        'PASSWORD': 'dummy',      
        'HOST': 'localhost',                 
        'PORT': '3306',                      
    }
}

# User profiles
AUTH_PROFILE_MODULE = 'stats.UserProfile'

# MongoDB settings
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_USER = 'sgrstats'
MONGODB_PASSWORD = 'dummy'
MONGODB_NAME = 'sgrstats'

# Celery queue
CARROT_BACKEND = 'ghettoq.taproot.Redis'

BROKER_HOST = 'localhost'	# Maps to redis host.
BROKER_PORT = 6379			# Maps to redis port.
BROKER_VHOST = '1'		# Maps to database name.

CELERYD_CONCURRENCY = 10	# Maximum of 8 concurrent workers

DATA_CACHE_PERIOD = 15 * 60 # 15 minutes
CACHE_PAGE_KEY_PREFIX = 'page_cache'
OLD_DATA_THRESHOLD = 2 # after how many days after player data is considered obsolete and should be purged

DEFAULT_FROM_EMAIL = 'info@sgrstats.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'info@sgrstats.com'
EMAIL_HOST_PASSWORD = 'dummy'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Cache settings
CACHE_BACKEND = 'redis_cache.cache://127.0.0.1:6379/?timeout=300'

# Signature generator settings
SIGNATURE_IMAGES_PATH = '/usr/local/www/domains/sgrstats.com/sig_images/'
SIGNATURE_IMAGES_URL = 'http://sig.sgrstats.com'
SIGNATURE_GENERATE_INTERVAL = 30 * 60 # Signature for each player will be generated once every 30 minutes
SIGNATURE_DATA_STALE_THRESHOLD = 30 * 60 # When player stats is older then 30 minutes it will be updated before creating the signature image

# Django grappelli
GRAPPELLI_ADMIN_TITLE = 'Stargate Stats Administration'

# Markupfield settings
MARKUP_FIELD_TYPES = {
    'markdown': markdown.markdown,
}

# Debug toolbar settings
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'cache_panel.CachePanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Ljubljana'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Append trailing slashes to URLs
APPEND_SLASH = True

# Prepend WWW to subdomains
PREPEND_WWW = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/usr/local/www/domains/sgrstats.com/releases/current/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www2.sgrstats.com'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'dummy'

# django-assets
ASSETS_AUTO_CREATE = True
ASSETS_DEBUG = False
ASSETS_EXPIRE = 'querystring'
YUI_COMPRESSOR_PATH = '/usr/local/bin/yuicompressor-2.4.2/build/yuicompressor-2.4.2.jar'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
#    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'lib.HttpOnlyCookie.HttpOnlyCookieMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    
    # Third-party
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

# Captcha
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)

ROOT_URLCONF = 'sgrstats.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
)

INSTALLED_APPS = (
    'core',
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.sitemaps',
    'django.contrib.comments',
    
    # Applications
    'accounts',
    'news',
    'articles',
    'polls',
    'stats',
    'rankings',
    'partners',
    'deals',
    'updates',
    
    # Third-party
    'celery',
    'captcha',
    'django_assets',
    'django_extensions',
    'registration',
    'taxonomy',
)

# Django-registration
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
