from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    return d.get(key)

@register.filter
def currency(value):
    try:
        return f"{int(float(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value

