import re
from random import sample

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse
from django.views import generic

from myshows.models import Show, Poster, PersonRole, NamedEntityOccurrence, Genre, Tag, Country


class ShowDetailView(generic.DetailView):
    model = Show

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posters'] = Poster.objects.filter(show=self.object)

        if 'season_number' in self.kwargs:
            season = self.object.season_set.filter(number=self.kwargs['season_number']).first()
        else:
            season = self.object.season_set.order_by('-number').prefetch_related(
                'episode_set', 'episode_set__episodecomment_set', 'episode_set__episodeimage_set').first()
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

        facts = sample(list(self.object.fact_set.all()), k=5) if self.object.fact_set.count() > 5 else self.object.fact_set.all()
        if 'fact' in self.request.GET:
            facts[0] = self.object.fact_set.get(pk=self.request.GET['fact'])

        for fact in facts:
            for occurrence in fact.entity_occurrences.all():
                fact.string = fact.string[:occurrence.position_start] + \
                                 f'''<a class="btn badge bg-occurrence" href="{
                                    reverse("named_entity", args=[occurrence.named_entity.id])
                                 }" id="occurrence-{occurrence.id}">{
                                    fact.string[occurrence.position_start:occurrence.position_end]
                                 }</a>''' + fact.string[occurrence.position_end:]

        context['facts'] = facts
        return context

    def get_object(self):
        return self.model.objects.filter(pk=self.kwargs['pk']).prefetch_related('genres', 'tags', 'fact_set__entity_occurrences__named_entity').get()


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
