import re

from django.core.cache import cache
from django.db.models import FloatField, Func, F, Avg, Count, ExpressionWrapper
from django.db.models.functions import Cast

from myshows.models import Show, Article, Fact, Review, PersonFact, Episode
from myshows.utils.named_entities import parse_html_text
from mysite.celery import app


@app.task
def process_show_description(show_id):
    """Task for processing Show object for Named Entities"""

    show = Show.objects.get(pk=show_id)
    show.entity_occurrences.all().delete()

    myshows_desc = re.search(r'\[Myshows](.+)\[\/Myshows]', show.description, re.DOTALL)
    if myshows_desc:
        parse_html_text(myshows_desc.group(1), show, myshows_desc.span(1)[0])

    kinopoisk_desc = re.search(r'\[Kinopoisk](.+)\[\/Kinopoisk]', show.description, re.DOTALL)
    if kinopoisk_desc:
        parse_html_text(kinopoisk_desc.group(1), show, kinopoisk_desc.span(1)[0])


@app.task
def process_fact_description(fact_id):
    """Task for processing Fact object for Named Entities"""
    fact = Fact.objects.get(pk=fact_id)
    fact.entity_occurrences.all().delete()
    parse_html_text(fact.string, fact)


@app.task
def process_review_description(review_id):
    """Task for processing Review object for Named Entities"""
    review = Review.objects.get(pk=review_id)
    review.entity_occurrences.all().delete()
    parse_html_text(review.description, review)


@app.task
def process_article_description(article_id):
    """Task for processing Article object for Named Entities"""
    article = Article.objects.get(pk=article_id)
    article.entity_occurrences.all().delete()
    parse_html_text(article.content, article)


@app.task
def process_person_fact_description(fact_id):
    """Task for processing PersonFact object for Named Entities"""
    fact = PersonFact.objects.get(pk=fact_id)
    fact.entity_occurrences.all().delete()
    parse_html_text(fact.string, fact)


@app.task
def update_cached_variables():
    """Task to update application cache"""
    episodecomment__count__avg = Episode.objects.order_by(  # reset ordering, because it replaces GROUP BY
    ).values(  # set values to force JOIN
        'episodecomment__id'
    ).annotate(
        episodecomment__count__avg=Cast(
            Func(F('id'), function='COUNT'),
            output_field=FloatField()
        ) / Func(
            Func(F('id'), function="DISTINCT"),
            function='COUNT', output_field=FloatField()
        )
    ).values_list('episodecomment__count__avg', flat=True)

    top_episodes = Episode.objects.annotate(
        dost_positive__avg=Avg('episodecomment__dost_positive'),
        dost_positive__count=Count('episodecomment__dost_positive'),
        dost_neutral__avg=Avg('episodecomment__dost_neutral'),
        dost_negative__avg=Avg('episodecomment__dost_negative'),
        dost_positive_index=ExpressionWrapper(
            (F('dost_positive__count') / (F('dost_positive__count') + episodecomment__count__avg)) *
            F('dost_positive__avg') / (
                    F('dost_positive__avg') +
                    F('dost_neutral__avg') +
                    F('dost_negative__avg')
            ),
            output_field=FloatField())
    ).filter(dost_positive__avg__isnull=False).order_by('-dost_positive_index')[:10]

    cache.set('top_episodes', list(top_episodes.values_list('id', flat=True)), None)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Function to setup periodic tasks"""
    sender.add_periodic_task(3600, update_cached_variables.s(), name='update every hour')
