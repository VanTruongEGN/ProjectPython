from django import template

register = template.Library()

@register.filter
def vnd(value):

    try:
        value = int(value)  # đảm bảo là số nguyên
        return "{:,} đ".format(value).replace(",", ".")
    except:
        return value