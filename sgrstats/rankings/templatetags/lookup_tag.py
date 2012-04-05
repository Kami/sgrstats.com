import re

from django.template import resolve_variable, Library

register = Library()

@register.filter
def lookup(value, key):
    return resolve_variable(key, value)

@register.filter
def format_weapon_name(value):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', value)