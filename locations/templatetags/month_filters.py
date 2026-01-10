import calendar
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def month_name(month_number):
    """
    Converts a month number (1-12) to its full name (January-December).
    """
    try:
        month_number = int(month_number)
        # Using calendar.month_name is simple and locale-aware
        return calendar.month_name[month_number]
    except (ValueError, IndexError):
        return ''

@register.filter
def month_name_short(month_number):
    """
    Converts a month number (1-12) to its short name (Jan-Dec).
    """
    try:
        month_number = int(month_number)
        # Or you can use datetime for more formatting options
        return timezone.datetime(2000, month_number, 1).strftime('%b')
    except (ValueError, IndexError):
        return ''
