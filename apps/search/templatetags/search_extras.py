from django import template
import json

register = template.Library()

@register.filter(name='parse_sports')
def parse_sports(profile):
    """Parse sports JSON field into a list"""
    try:
        sports = json.loads(profile.sports or '[]')
        return sports if isinstance(sports, list) else []
    except (json.JSONDecodeError, AttributeError):
        return []