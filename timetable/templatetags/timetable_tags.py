from django import template

register = template.Library()


@register.filter
def get_item(value, key):
    if value:
        return value.get(key)
    return None