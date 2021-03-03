from django.views import generic

from myshows.models import Person


class PersonDetailView(generic.DetailView):
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self):
        return self.model.objects.filter(pk=self.kwargs['pk']).prefetch_related('personimage_set').get()
