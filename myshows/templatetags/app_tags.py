from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from myshows.models import Show, Fact, Review, Article

register = template.Library()


@register.simple_tag
def get_url_for_named_entity_content(occurrence):
    url = ''
    if occurrence.content_type == ContentType.objects.get_for_model(Show):
        url = reverse("detail", args=[occurrence.object_id])
    elif occurrence.content_type == ContentType.objects.get_for_model(Fact):
        url = reverse("detail", args=[occurrence.content_object.show.id]) + f"?fact={occurrence.object_id}"
    elif occurrence.content_type == ContentType.objects.get_for_model(Review):
        url = reverse("detail", args=[occurrence.content_object.show.id]) + f"?review={occurrence.object_id}"
    elif occurrence.content_type == ContentType.objects.get_for_model(Article):
        url = reverse("news_detail", args=[occurrence.object_id])

    return url + f'#occurrence-{occurrence.id}'


@register.simple_tag
def get_model_name(item):
    return item._meta.model_name
