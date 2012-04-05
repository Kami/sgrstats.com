import os
import sys
import django.core.handlers.wsgi

# Put the Django project on system path
root_path = os.path.abspath(os.path.dirname(__file__) + '../../../')
sys.path.insert(0, os.path.join(root_path, 'sgrstats'))
sys.path.insert(0, root_path)

os.environ['HOME'] = '/usr/local/www/domains/sgrstats.com/'
os.environ['DJANGO_SETTINGS_MODULE'] = 'sgrstats.settings'
os.environ['JAVA_HOME'] = '/usr/local/'

application = django.core.handlers.wsgi.WSGIHandler()