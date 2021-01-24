from django.core.paginator import Paginator
from django.db.models import Count, Avg, F, Sum
from django.shortcuts import render
from django.views import generic

from myshows.models import Show, Poster, Article, Country, Genre, Tag


def index(request):
    shows = Show.objects.order_by('-myshows_rating').all()[:10]
    news = Article.objects.all()
    page = request.GET.get('page', 1)
    return render(request, 'index.html', context={'shows': shows, 'news_list': Paginator(news, 5).page(page)})


class ShowDetailView(generic.DetailView):
    model = Show

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posters'] = Poster.objects.filter(show=self.object)
        return context

    def get_object(self):
        return self.model.objects.filter(pk=self.kwargs['pk']).prefetch_related('genres', 'tags').get()


class ShowListView(generic.ListView):
    model = Show
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'all'
        return context


class SearchShowListView(generic.ListView):
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET['q']
        return Show.objects.filter(title_ru__icontains=query)


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
