import re

from myshows.models import Show, Article, Fact, Review
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
