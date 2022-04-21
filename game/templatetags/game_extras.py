from django import template

register = template.Library()

@register.filter(name='sub')
def sub(x, y):
    return x - y