import re

from django.contrib.contenttypes.models import ContentType

from mysite.celery import app
from myshows.models import Show, Article, Fact, Review, NamedEntityOccurrence, NamedEntity
from myshows.utils.named_entities import parse_html_text


def clear_db_entities(content_object):
    NamedEntityOccurrence.objects.filter(
        content_type=ContentType.objects.get_for_model(content_object),
        object_id=content_object.id).delete()


@app.task
def process_show_description(show_id):
    show = Show.objects.get(pk=show_id)
    clear_db_entities(show)

    myshows_desc = re.search(r'\[Myshows](.+)\[\/Myshows]', show.description, re.DOTALL)
    if myshows_desc:
        parse_html_text(myshows_desc.group(1), show, myshows_desc.span(1)[0])

    kinopoisk_desc = re.search(r'\[Kinopoisk](.+)\[\/Kinopoisk]', show.description, re.DOTALL)
    if kinopoisk_desc:
        parse_html_text(kinopoisk_desc.group(1), show, kinopoisk_desc.span(1)[0])


@app.task
def process_fact_description(fact_id):
    fact = Fact.objects.get(pk=fact_id)
    clear_db_entities(fact)
    parse_html_text(fact.string, fact)


@app.task
def process_review_description(review_id):
    review = Review.objects.get(pk=review_id)
    clear_db_entities(review)
    parse_html_text(review.description, review)


@app.task
def process_article_description(article_id):
    article = Article.objects.get(pk=article_id)
    clear_db_entities(article)
    parse_html_text(article.content, article)
