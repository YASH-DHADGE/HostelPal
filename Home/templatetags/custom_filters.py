from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary using the key"""
    if dictionary is None:
        return None
    return dictionary.get(key, '')

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate what percentage value is of total"""
    try:
        return float(value) / float(total) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def to_int(value):
    """Convert a float to an integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

@register.filter
def findall(queryset, attr_value_pair):
    """
    Filter a queryset by attribute value pair
    Usage: attendances|findall:'status,present'
    """
    attr, value = attr_value_pair.split(',')
    result = []
    for item in queryset:
        item_value = getattr(item, attr, None)
        if item_value == value:
            result.append(item)
    return result 