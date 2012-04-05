from django.conf import settings
from pymongo.connection import Connection

connection = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)
database = connection[settings.MONGODB_NAME]