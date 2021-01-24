from django import template

register = template.Library()


# Calls .getlist() on a querydict
# Use: querydict | get_list {{ querydict|get_list:"itemToGet" }}
@register.filter
def get_list(query_dict, item_to_get):
    return query_dict.getlist(item_to_get)
