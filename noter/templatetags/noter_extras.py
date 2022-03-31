from datetime import datetime, date, timedelta, timezone
from django import template

register = template.Library()

@register.filter(name='date_diff')
def date_diff(a_date):
    today = datetime.now().date() - timedelta(days=1)
    diff = (a_date - today).days

    return abs(diff)