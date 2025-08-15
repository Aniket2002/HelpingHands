from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}

@register.filter
def get_day_enabled(schedule_data, day):
    """Get whether a day is enabled in schedule data"""
    if schedule_data and isinstance(schedule_data, dict):
        day_data = schedule_data.get(day, {})
        return day_data.get('enabled', False)
    return False

@register.filter 
def get_day_start(schedule_data, day):
    """Get start time for a day"""
    if schedule_data and isinstance(schedule_data, dict):
        day_data = schedule_data.get(day, {})
        return day_data.get('start_time', '09:00')
    return '09:00'

@register.filter
def get_day_end(schedule_data, day):
    """Get end time for a day"""
    if schedule_data and isinstance(schedule_data, dict):
        day_data = schedule_data.get(day, {})
        return day_data.get('end_time', '17:00')
    return '17:00'
