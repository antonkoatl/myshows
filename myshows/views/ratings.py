from django.db.models import F, Avg, Sum, Count
from django.views import generic

from myshows.models import Country, Genre, Tag


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
