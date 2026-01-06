from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return None

@register.filter
def currency(value):
    try:
        return f"{int(float(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value

