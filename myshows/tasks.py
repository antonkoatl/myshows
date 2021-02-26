import re

from django.contrib.contenttypes.models import ContentType

from mysite.celery import app
from myshows.models import Show, Article, Fact, Review, NamedEntityOccurrence, NamedEntity
from myshows.utils.named_entities import parse_html_text


@app.task
def add(x, y):
    return x + y


def clear_db_entities(content_object):
    NamedEntityOccurrence.objects.filter(
        content_type=ContentType.objects.get_for_model(content_object),
        object_id=content_object.id).delete()
    NamedEntity.objects.filter(namedentityoccurrence=None).delete()


@app.task
def process_show_description(show_id):
    show = Show.objects.get(pk=show_id)
    clear_db_entities(show)
    description_marked = ""

    myshows_desc = re.search(r'\[Myshows](.+)\[\/Myshows]', show.description, re.DOTALL)
    if myshows_desc:
        description_marked += '<p>' + parse_html_text(myshows_desc.group(1), show) + '</p>'

    kinopoisk_desc = re.search(r'\[Kinopoisk](.+)\[\/Kinopoisk]', show.description, re.DOTALL)
    if kinopoisk_desc:
        description_marked += '<hr>'
        description_marked += '<p>' + parse_html_text(kinopoisk_desc.group(1), show) + '</p>'

    show.description_marked = description_marked
    show.save()


@app.task
def process_article_description(article_id):
    article = Article.objects.get(pk=article_id)
    clear_db_entities(article)
    article.content_marked = parse_html_text(article.content, article)
    article.save()


@app.task
def process_fact_description(fact_id):
    fact = Fact.objects.get(pk=fact_id)
    clear_db_entities(fact)
    fact.string_marked = parse_html_text(fact.string, fact)
    fact.save()


@app.task
def process_review_description(review_id):
    review = Review.objects.get(pk=review_id)
    clear_db_entities(review)
    review.description_marked = parse_html_text(review.description, review)
    review.save()
