from django.views import generic

from myshows.models import Person
from myshows.utils.utils import sample_facts


class PersonDetailView(generic.DetailView):
    model = Person
    queryset = Person.objects.prefetch_related('personrole_set__show__poster_set')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facts'] = sample_facts(self.object.personfact_set.prefetch_related('entity_occurrences__named_entity'), self.request.GET.get('fact', None))
        return context
