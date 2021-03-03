from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.views import generic

from myshows.models import Article, NamedEntityOccurrence


class NewsListView(generic.ListView):
    model = Article
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active'] = 'news'
        return context


class NewsDetailView(generic.DetailView):
    model = Article

    def get_object(self, **kwargs):
        object = super().get_object(**kwargs)
        content = object.content

        for occurrence in NamedEntityOccurrence.objects.filter(
                content_type=ContentType.objects.get_for_model(Article),
                object_id=object.id).order_by('-position_start'):
            content = content[:occurrence.position_start] + \
                                 f'''<a class="btn badge bg-occurrence" href="{
                                 reverse("named_entity", args=[occurrence.named_entity.id])
                                 }" id="occurrence-{occurrence.id}">{
                                 content[occurrence.position_start:occurrence.position_end]
                                 }</a>''' + content[occurrence.position_end:]

        object.content = content
        return object
