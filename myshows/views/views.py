from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import generic

from myshows.models import Show, Poster, Article


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
        return context
