
from django import template

register = template.Library()

@register.filter
def minus(value, arg):
    try:
        return int(float(value) - float(arg))
    except:
        return 0
