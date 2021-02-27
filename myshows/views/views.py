from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Count, Avg, F, Sum
from django.http import JsonResponse
from django.views import generic

from myshows.models import Country, Genre, Tag
from myshows.models.article import Article
from myshows.models.named_entity import NamedEntity, NamedEntityOccurrence
from myshows.models.person import PersonRole
from myshows.models.show import Poster, Show, Fact, Review
from myshows.utils.trivia_helper import get_new_question


def check_trivia(request):
    result = {}

    if 'answer' in request.POST:
        correct = request.session['trivia']['question']['correct_answer_num']
        answer = int(request.POST['answer'])

        if answer == correct:
            request.session['trivia']['score'] += 1
            result['result'] = True
        else:
            request.session['trivia']['score'] -= 1
            result['result'] = False

        result['score'] = request.session['trivia']['score']
        result['correct_answer'] = request.session['trivia']['question']['correct_answer_num']

        mode = request.session['trivia']['mode']
        new_question = get_new_question(mode)
        request.session['trivia']['question'] = new_question

        result['question'] = {
                'type':  new_question['type'],
                'image': new_question['image_url'],
                'variants': new_question['text_variants']
            }

        request.session.modified = True

    elif 'mode' in request.POST:
        mode = request.POST['mode']
        request.session['trivia']['mode'] = mode
        new_question = get_new_question(mode)
        request.session['trivia']['question'] = new_question

        result['question'] = {
            'type': new_question['type'],
            'image': new_question['image_url'],
            'variants': new_question['text_variants']
        }

        request.session.modified = True

    return JsonResponse(result, status=200)


class IndexView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shows = Show.objects.order_by('-myshows_rating').all()[:10]
        news = Article.objects.all()
        page = self.request.GET.get('page', 1)

        context['shows'] = shows
        context['news'] = Paginator(news, 5).page(page)
        return context


class ShowDetailView(generic.DetailView):
    model = Show

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posters'] = Poster.objects.filter(show=self.object)

        if 'season_number' in self.kwargs:
            season = self.object.season_set.filter(number=self.kwargs['season_number']).first()
        else:
            season = self.object.season_set.order_by('-number').first()
        context['season'] = season

        context['actor_roles'] = self.object.personrole_set.filter(role=PersonRole.RoleType.ACTOR)[:5]

        if 'review' in self.request.GET:
            review_id = self.request.GET['review']
            context['reviews'] = Paginator(self.object.review_set.filter(id=review_id), 5).page(1)
        else:
            page = self.request.GET.get('page', 1)
            context['reviews'] = Paginator(self.object.review_set.all(), 5).page(page)

        return context

    def get_object(self):
        return self.model.objects.filter(pk=self.kwargs['pk']).prefetch_related('genres', 'tags').get()


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


class NewsListView(generic.ListView):
    model = Article
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'news'
        return context


class NewsDetailView(generic.DetailView):
    model = Article


class RatingsDetailView(generic.TemplateView):
    template_name = "ratings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'ratings'

        context['show_countries_count'] = {
            'title': 'Страны по количеству',
            'data': Country.objects.annotate(shows_data=Count('show')).order_by('-shows_data')[:5].annotate(
                title=F('name_ru')).prefetch_related('show_set')
        }
        context['show_countries_rating'] = {
            'title': 'Страны по среднему рейтингу',
            'data': Country.objects.filter(show__myshows_rating__isnull=False).annotate(
                shows_data=Avg('show__myshows_rating')).order_by('-shows_data')[:5].annotate(
                title=F('name_ru')).prefetch_related('show_set')
        }
        context['show_genres_watching'] = {
            'title': 'Жанры по количеству смотрящих',
            'data': Genre.objects.filter(show__myshows_watching__isnull=False).annotate(
                shows_data=Sum('show__myshows_watching')
                ).order_by('-shows_data')[:5].prefetch_related('show_set')
        }
        context['show_tags_watching'] = {
            'title': 'Тэги по среднему рейтингу',
            'data': Tag.objects.filter(show__myshows_rating__isnull=False).annotate(
                shows_data=Avg('show__myshows_rating')).order_by('-shows_data')[:5].prefetch_related('show_set')
        }

        return context


class TriviaView(generic.TemplateView):
    template_name = "trivia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'trivia'

        if 'trivia' not in self.request.session:
            self.request.session['trivia'] = {'score': 0}

        mode = self.request.session['trivia'].get('mode', 'all')
        question = get_new_question(mode)

        context['mode'] = mode
        context['score'] = self.request.session['trivia']['score']
        context['question'] = {
            'type': question['type'],
            'image': question['image_url'],
            'variants': question['text_variants']
        }

        self.request.session['trivia']['mode'] = mode
        self.request.session['trivia']['question'] = question
        self.request.session.modified = True
        return context


class NamedEntityView(generic.DetailView):
    model = NamedEntity

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        similary_entities = NamedEntity.objects.annotate(
            similarity=TrigramSimilarity('name', self.object.name)).exclude(id=self.object.id).order_by('-similarity')[:10]

        context['similary_entities'] = similary_entities

        page = self.request.GET.get('page', 1)
        page_obj = Paginator(self.object.namedentityoccurrence_set.all(), 50).page(page)
        context['page_obj'] = page_obj

        shows = {}

        page_occurrences = NamedEntityOccurrence.objects.filter(id__in=page_obj.object_list).prefetch_related('content_object')

        for occurrence in page_occurrences.filter(content_type=ContentType.objects.get_for_model(Fact)):
            fact = occurrence.content_object
            if fact.show.id not in shows:
                shows[fact.show.id] = fact.show
                shows[fact.show.id].display_data = [occurrence]
            else:
                shows[fact.show.id].display_data.append(occurrence)

        for occurrence in page_occurrences.filter(content_type=ContentType.objects.get_for_model(Review)):
            review = occurrence.content_object
            if review.show.id not in shows:
                shows[review.show.id] = review.show
                shows[review.show.id].display_data = [occurrence]
            else:
                shows[review.show.id].display_data.append(occurrence)

        for occurrence in page_occurrences.filter(content_type=ContentType.objects.get_for_model(Show)):
            show = occurrence.content_object
            if show.id not in shows:
                shows[show.id] = show
                shows[show.id].display_data = [occurrence]
            else:
                shows[show.id].display_data.append(occurrence)

        context['shows'] = shows.values()

        return context


class TestView(generic.TemplateView):
    template_name = 'test.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['actor_roles'] = Show.objects.get(pk=1).personrole_set.filter(role=PersonRole.RoleType.ACTOR)[:5]
        return context
