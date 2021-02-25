from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


# Calls .getlist() on a querydict
# Use: querydict | get_list {{ querydict|get_list:"itemToGet" }}
@register.filter
def get_list(query_dict, item_to_get):
    return query_dict.getlist(item_to_get)


@register.filter
def percentage(value, div=1):
    return str(100 * value / div if div != 0 else 0)


@register.filter
def content_type(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj)
