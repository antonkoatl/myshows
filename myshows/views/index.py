from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.views import generic

from myshows.models import Show, Article, NamedEntity, Episode


class IndexView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shows = Show.objects.order_by('-myshows_rating')[:10]
        news = Article.objects.prefetch_related('articleimage_set')
        page = self.request.GET.get('page', 1)

        context['shows'] = shows
        context['news'] = Paginator(news, 5).page(page)

        context['top_places'] = NamedEntity.objects.filter(type=NamedEntity.Type.LOCATION).annotate(
            refs_count=Count('namedentityoccurrence')).order_by('-refs_count')[:10]
        context['top_persons'] = NamedEntity.objects.filter(type=NamedEntity.Type.PERSON).annotate(
            refs_count=Count('namedentityoccurrence')).order_by('-refs_count')[:10]
        context['top_organizations'] = NamedEntity.objects.filter(type=NamedEntity.Type.ORGANIZATION).annotate(
            refs_count=Count('namedentityoccurrence')).order_by('-refs_count')[:10]
        context['top_misc'] = NamedEntity.objects.filter(type=NamedEntity.Type.MISC).annotate(
            refs_count=Count('namedentityoccurrence')).order_by('-refs_count')[:10]

        context['top_episodes'] = Episode.objects.filter(
            id__in=cache.get('top_episodes')
        ).annotate(
            dost_positive__avg=Avg('episodecomment__dost_positive'),
            dost_neutral__avg=Avg('episodecomment__dost_neutral'),
            dost_negative__avg=Avg('episodecomment__dost_negative')
        ).select_related('season__show').prefetch_related('episodecomment_set')

        return context
