from django.shortcuts import render
from django.views import generic

from myshows.models import Show, Poster


def index(request):
    shows = Show.objects.order_by('-myshows_rating').all()[:10]
    return render(request, 'index.html', context={'shows': shows})


class ShowDetailView(generic.DetailView):
    model = Show

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posters'] = Poster.objects.filter(show=self.object)
        return context

    def get_object(self):
        return self.model.objects.filter(pk=self.kwargs['pk']).prefetch_related('genres', 'tags').get()
