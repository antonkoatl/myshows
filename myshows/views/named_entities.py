import re
from itertools import zip_longest, chain

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.views import generic

from myshows.models import NamedEntity, NamedEntityOccurrence, Fact, Review, Show, Article, PersonFact


class NamedEntityView(generic.DetailView):
    model = NamedEntity

    def append_occurrence(self, data, item, text, occurrence):
        left_width = 100
        right_width = 100

        window_left = text[max(occurrence.position_start - left_width, 0):occurrence.position_start]
        window_right = text[occurrence.position_end:occurrence.position_end + right_width]

        i = occurrence.position_start - left_width - 1
        while 0 <= i < occurrence.position_start and not text[i].isspace():
            i += 1
        window_left = window_left[i - (occurrence.position_start - left_width - 1):]

        i = occurrence.position_end + right_width
        while len(text) > i > occurrence.position_end and not text[i].isspace():
            i -= 1
        window_right = window_right[:-(occurrence.position_end + right_width - i) or None]

        occurrence.window_left = re.sub(r'\[\/?(Kinopoisk|Myshows)]', '', window_left)
        occurrence.window_right = re.sub(r'\[\/?(Kinopoisk|Myshows)]', '', window_right)
        occurrence.window_text = text[occurrence.position_start:occurrence.position_end]

        if item.id not in data:
            data[item.id] = item
            data[item.id].display_data = [occurrence]
        else:
            data[item.id].display_data.append(occurrence)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        similary_entities = NamedEntity.objects.annotate(
            similarity=TrigramSimilarity('name', self.object.name)).exclude(id=self.object.id).order_by('-similarity')[:10]

        context['similary_entities'] = similary_entities

        page = self.request.GET.get('page', 1)
        page_obj = Paginator(self.object.namedentityoccurrence_set.all(), 50).page(page)
        context['page_obj'] = page_obj

        shows = {}
        articles = {}
        persons = {}

        page_occurrences = NamedEntityOccurrence.objects.filter(id__in=page_obj.object_list).prefetch_related('content_object')

        for occurrence in page_occurrences:
            if occurrence.content_type == ContentType.objects.get_for_model(Fact):
                self.append_occurrence(shows, occurrence.content_object.show, occurrence.content_object.string, occurrence)
            elif occurrence.content_type == ContentType.objects.get_for_model(Review):
                self.append_occurrence(shows, occurrence.content_object.show, occurrence.content_object.description, occurrence)
            elif occurrence.content_type == ContentType.objects.get_for_model(Show):
                self.append_occurrence(shows, occurrence.content_object, occurrence.content_object.description, occurrence)
            elif occurrence.content_type == ContentType.objects.get_for_model(Article):
                self.append_occurrence(articles, occurrence.content_object, occurrence.content_object.content, occurrence)
            elif occurrence.content_type == ContentType.objects.get_for_model(PersonFact):
                self.append_occurrence(persons, occurrence.content_object.person, occurrence.content_object.string, occurrence)

        context['items'] = filter(lambda x: x is not None, chain(*zip_longest(shows.values(), articles.values(), persons.values())))

        return context
