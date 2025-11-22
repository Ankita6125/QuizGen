from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Custom filter to safely get dictionary value by key"""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return 0
