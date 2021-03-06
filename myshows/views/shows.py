import re

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Avg
from django.urls import reverse
from django.views import generic

from myshows.models import Show, Poster, PersonRole, NamedEntityOccurrence, Genre, Tag, Country, Episode
from myshows.utils.utils import sample_facts


class ShowDetailView(generic.DetailView):
    model = Show
    queryset = Show.objects.prefetch_related('genres', 'tags', 'fact_set__entity_occurrences__named_entity')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posters'] = Poster.objects.filter(show=self.object)

        season_set = self.object.season_set.order_by('-number').prefetch_related(
            Prefetch('episode_set', queryset=Episode.objects.annotate(
                dost_positive__avg=Avg('episodecomment__dost_positive'),
                dost_neutral__avg=Avg('episodecomment__dost_neutral'),
                dost_negative__avg=Avg('episodecomment__dost_negative')
            ).prefetch_related('episodeimage_set'))
        )

        if 'season_number' in self.kwargs:
            season = season_set.filter(number=self.kwargs['season_number']).first()
        else:
            season = season_set.first()
        context['season'] = season

        context['actor_roles'] = self.object.personrole_set.filter(role=PersonRole.RoleType.ACTOR).select_related('person')[:5]

        if 'review' in self.request.GET:
            review_id = self.request.GET['review']
            context['reviews'] = Paginator(self.object.review_set.prefetch_related('entity_occurrences', 'entity_occurrences__named_entity').filter(id=review_id), 5).page(1)
        else:
            page = self.request.GET.get('page', 1)
            context['reviews'] = Paginator(self.object.review_set.prefetch_related('entity_occurrences', 'entity_occurrences__named_entity'), 5).page(page)

        description_marked = self.object.description

        for occurrence in NamedEntityOccurrence.objects.filter(
                content_type=ContentType.objects.get_for_model(Show),
                object_id=self.object.id).order_by('-position_start').select_related('named_entity'):
            description_marked = description_marked[:occurrence.position_start] + \
                                 f'''<a class="btn badge bg-occurrence" href="{
                                    reverse("named_entity", args=[occurrence.named_entity.id])
                                 }" id="occurrence-{occurrence.id}">{
                                    description_marked[occurrence.position_start:occurrence.position_end]
                                 }</a>''' + description_marked[occurrence.position_end:]

        description = ''
        myshows_desc = re.search(r'\[Myshows](.+)\[\/Myshows]', description_marked, re.DOTALL)
        if myshows_desc:
            description += '<p>' + myshows_desc.group(1) + '</p>'

        kinopoisk_desc = re.search(r'\[Kinopoisk](.+)\[\/Kinopoisk]', description_marked, re.DOTALL)
        if kinopoisk_desc:
            description += '<hr>'
            description += '<p>' + kinopoisk_desc.group(1) + '</p>'

        self.object.description = description

        for review in context['reviews']:
            for occurrence in review.entity_occurrences.all():
                review.description = review.description[:occurrence.position_start] + \
                                 f'''<a class="btn badge bg-occurrence" href="{
                                    reverse("named_entity", args=[occurrence.named_entity.id])
                                 }" id="occurrence-{occurrence.id}">{
                                    review.description[occurrence.position_start:occurrence.position_end]
                                 }</a>''' + review.description[occurrence.position_end:]



        context['facts'] = sample_facts(self.object.fact_set.all(), self.request.GET.get('fact', None))
        return context


class ShowListView(generic.ListView):
    model = Show
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'all'

        context['genres'] = Genre.objects.annotate(shows_count=Count('show')).order_by('-shows_count')
        context['tags'] = Tag.objects.annotate(shows_count=Count('show')).order_by('-shows_count')
        context['years'] = Show.objects.values('year').annotate(shows_count=Count('year')).order_by('-year')
        context['countries'] = Country.objects.annotate(shows_count=Count('show')).order_by('-shows_count')
        context['categories'] = Show.objects.values('category').annotate(
            shows_count=Count('category')).order_by('-shows_count')
        context['types'] = Show.objects.values('type').annotate(
            shows_count=Count('type')).order_by('-shows_count')

        for item in context['categories']:
            item['category_label'] = Show.ShowCategories(item['category']).label
        for item in context['types']:
            item['type_label'] = Show.ShowTypes(item['type']).label

        context['request'] = self.request
        return context

    def get_queryset(self):
        shows = Show.objects.all()

        if 'q' in self.request.GET:
            shows = shows.filter(title_ru__icontains=self.request.GET['q'])

        for genre in self.request.GET.getlist('genre'):
            shows = shows.filter(genres=genre)

        for tag in self.request.GET.getlist('tag'):
            shows = shows.filter(tags=tag)

        if 'year' in self.request.GET:
            shows = shows.filter(year__in=self.request.GET.getlist('year'))

        if 'country' in self.request.GET:
            shows = shows.filter(country__in=self.request.GET.getlist('country'))

        if 'category' in self.request.GET:
            shows = shows.filter(category__in=self.request.GET.getlist('category'))

        if 'type' in self.request.GET:
            shows = shows.filter(type__in=self.request.GET.getlist('type'))

        return shows
