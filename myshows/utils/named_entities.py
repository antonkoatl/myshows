import math
import re
from itertools import chain
from pprint import pprint

import spacy
from bs4 import BeautifulSoup, NavigableString
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from myshows.models import Show, Fact, Review, Article
from myshows.models.named_entity import NamedEntity, NamedEntityOccurrence

nlp_ru = spacy.load("ru_core_news_lg")
nlp_en = spacy.load("en_core_web_lg")
nlp_xx = spacy.load("xx_ent_wiki_sm")


entity_types = {
    'PERSON': 'PER',
    'PERCENT': 'PRC',
    'DATE': 'DAT',
    'TIME': 'TIM',
    'MISC': 'MIS',
    'CARDINAL': 'CAR',
}


def merge_ents(*doc_ents):
    ents = []

    for entity_new in chain(*doc_ents):
        if entity_new.label_ == "MONEY": continue
        if entity_new.label_ == "QUANTITY": continue

        found = False
        for entity in ents:
            if entity.start_char == entity_new.start_char or entity.end_char == entity_new.end_char:
                if len(entity.lemma_) == 0 and len(entity_new.lemma_) > 0:
                    ents.remove(entity)
                    ents.append(entity_new)

                found = True
                break

        if not found:
            ents.append(entity_new)

    # pprint([[ent.text, ent.label_, ent.lemma_] for ent in ents])
    return ents


def get_lemma(entity):
    if len(entity.lemma_) > 0:
        return entity.lemma_.lower().strip()
    else:
        return entity.text.lower().strip()


def parse_ner_text(text, content_object):
    current_pos = 0
    doc_ru = nlp_ru(text)
    doc_en = nlp_en(text)
    doc_xx = nlp_xx(text)
    description_marked = ''

    ents_all = merge_ents(
        doc_ru.ents,
        filter(lambda x: x.label_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'CARDINAL'], doc_en.ents),
        filter(lambda x: x.label_ == 'MISC', doc_xx.ents))

    for entity in ents_all:
        entity_db = process_founded_entity(entity, content_object)

        description_marked += text[current_pos:entity.start_char]
        description_marked += f'<a href="{reverse("named_entity", args=[entity_db.id])}" ' \
                              f'class="badge bg-info">{entity.text}</a>'
        current_pos = entity.end_char

    if len(ents_all) > 0:
        description_marked += text[current_pos:]
    else:
        description_marked = text

    return description_marked


def get_url_for_named_entity_content(occurrence):
    url = ''
    if occurrence.content_type == ContentType.objects.get_for_model(Show):
        url = reverse("detail", args=[occurrence.object_id])
    elif occurrence.content_type == ContentType.objects.get_for_model(Fact):
        url = reverse("detail", args=[occurrence.content_object.show.id])
    elif occurrence.content_type == ContentType.objects.get_for_model(Review):
        url = reverse("detail", args=[occurrence.content_object.show.id]) + f"?review={occurrence.object_id}"
    elif occurrence.content_type == ContentType.objects.get_for_model(Article):
        url = reverse("news_detail", args=[occurrence.object_id])

    return url + f'#occurrence-{occurrence.id}'


def process_founded_entity(entity, content_object, text):
    entity_db = NamedEntity.objects.filter(lemma__lemma=get_lemma(entity)).first()

    if not entity_db:
        entity_db = NamedEntity(name=entity.text.strip(),
                                type=NamedEntity.Type(entity_types.get(entity.label_, entity.label_)))
        entity_db.save()
        entity_db.lemma_set.create(lemma=get_lemma(entity))

    occurrence_db = NamedEntityOccurrence.objects.filter(
        named_entity=entity_db,
        content_type=ContentType.objects.get_for_model(content_object),
        object_id=content_object.id).first()

    if not occurrence_db:
        occurrence_db = NamedEntityOccurrence(
            named_entity=entity_db,
            content_object=content_object,
            occurrence_context='',
        )
        occurrence_db.save()

        text_context = f'<a href="{get_url_for_named_entity_content(occurrence_db)}" class="badge bg-danger">' + entity.text + '</a>'
        left_space_half = math.floor(
            (NamedEntityOccurrence._meta.get_field('occurrence_context').max_length - len(text_context)) / 2)
        text_context = text[entity.start_char - left_space_half:entity.start_char] + text_context + text[
                                                                                                    entity.end_char:entity.end_char + left_space_half]

        i = entity.start_char - left_space_half - 1
        while 0 <= i < entity.start_char and not text[i].isspace():
            i += 1
        text_context = text_context[i - (entity.start_char - left_space_half - 1):]

        i = entity.end_char + left_space_half
        while len(text) > i > entity.end_char and not text[i].isspace():
            i -= 1
        text_context = text_context[:-(entity.end_char + left_space_half - i) or None]

        occurrence_db.occurrence_context = text_context
        occurrence_db.save()

    return entity_db, occurrence_db


def parse_ner_soup(text_node, content_object, soup):
    current_pos = 0
    text = str(text_node)
    doc_ru = nlp_ru(text)
    doc_en = nlp_en(text)
    doc_xx = nlp_xx(text)

    ents_all = merge_ents(
            doc_ru.ents,
            filter(lambda x: x.label_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'CARDINAL'], doc_en.ents),
            filter(lambda x: x.label_ == 'MISC', doc_xx.ents))

    ents_all.sort(key=lambda x: x.start_char)

    for entity in ents_all:
        entity_db, occurrence_db = process_founded_entity(entity, content_object, text)

        text_node.insert_before(text[current_pos:entity.start_char])
        a_tag = soup.new_tag("a", attrs={
            "class": "badge bg-info",
            "href": reverse("named_entity", args=[entity_db.id]),
            "id": f"occurrence-{occurrence_db.id}"
        })
        a_tag.string = entity.text
        text_node.insert_before(a_tag)
        current_pos = entity.end_char

    if len(ents_all) > 0:
        text_node.insert_before(text[current_pos:])
        text_node.extract()


def recursive_soup_process(node, content_object, soup):
    for element in list(node):
        if isinstance(element, NavigableString):
            parse_ner_soup(element, content_object, soup)
        else:
            if element.name == 'script': continue
            recursive_soup_process(element, content_object, soup)


def parse_html_text(html_text, content_object):
    soup = BeautifulSoup(html_text, 'html.parser')
    recursive_soup_process(soup, content_object, soup)
    return str(soup)


def mark_description(show):
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
