import random

from django.core.paginator import Paginator
from django.db.models import Count, Avg, F, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic

from myshows.models import Show, Poster, Article, Country, Genre, Tag, Episode


def index(request):
    shows = Show.objects.order_by('-myshows_rating').all()[:10]
    news = Article.objects.all()
    page = request.GET.get('page', 1)
    return render(request, 'index.html', context={'shows': shows, 'news_list': Paginator(news, 5).page(page)})


def check_trivia(request):
    correct = request.session['correct']
    answer = request.POST['answer']

    if answer == correct:
        if 'score' in request.session:
            request.session['score'] += 1
        else:
            request.session['score'] = 1
        return JsonResponse({'result': True, 'score': request.session['score']}, status=200)
    else:
        if 'score' in request.session:
            request.session['score'] -= 1
        else:
            request.session['score'] = -1
        return JsonResponse({'result': False, 'score': request.session['score']}, status=200)


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

        episodes = []
        max_id = Episode.objects.last().id


        while len(episodes) < 4:
            pk = random.randrange(max_id)
            ep = Episode.objects.filter(pk=pk)
            if ep.exists() and ep.get().episodeimage_set.first(): episodes.append(ep.get())

        correct = random.choice(episodes)
        random.shuffle(episodes)
        variants = [x.season.show.title_ru for x in episodes]

        context['question'] = {
            'image': correct.episodeimage_set.first().image,
            'variants': variants
        }

        if 'score' not in self.request.session:
            self.request.session['score'] = 0

        context['score'] = self.request.session['score']

        self.request.session['correct'] = correct.season.show.title_ru

        return context
