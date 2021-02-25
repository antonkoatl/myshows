import re
from itertools import chain
from pprint import pprint

import spacy
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from myshows.models import NamedEntity, NamedEntityOccurrence

nlp_ru = spacy.load("ru_core_news_lg")
nlp_en = spacy.load("en_core_web_lg")
nlp_xx = spacy.load("xx_ent_wiki_sm")


entity_types = {
    'PERSON': 'PER',
    'PERCENT': 'PRC',
    'DATE': 'DAT',
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

    pprint([[ent.text, ent.label_, ent.lemma_] for ent in ents])
    return ents


def get_lemma(entity):
    if len(entity.lemma_) > 0:
        return entity.lemma_.lower()
    else:
        return entity.text.lower()


def parse_ner(text, show):
    current_pos = 0
    doc_ru = nlp_ru(text)
    doc_en = nlp_en(text)
    doc_xx = nlp_xx(text)
    description_marked = ''

    for entity in merge_ents(
            doc_ru.ents,
            filter(lambda x: x.label_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'CARDINAL'], doc_en.ents),
            filter(lambda x: x.label_ == 'MISC', doc_xx.ents)):
        entity_db = NamedEntity.objects.filter(lemma=get_lemma(entity)).first()

        if not entity_db:
            entity_db = NamedEntity(lemma=get_lemma(entity), type=NamedEntity.Type(entity_types.get(entity.label_, entity.label_)))
            entity_db.save()

        occurrence = NamedEntityOccurrence.objects.filter(
            named_entity=entity_db,
            content_type=ContentType.objects.get_for_model(show),
            object_id=show.id).first()

        if not occurrence:
            occurrence = NamedEntityOccurrence(named_entity=entity_db, content_object=show)
            occurrence.save()

        description_marked += text[current_pos:entity.start_char]
        description_marked += f'<a href="{reverse("named_entity", args=[entity_db.id])}" ' \
                              f'class="badge bg-info">{entity.text}</a>'
        current_pos = entity.end_char

    if len(doc_ru.ents) > 0:
        description_marked += text[current_pos:]
    else:
        description_marked = text

    return description_marked


def mark_description(show):
    description_marked = ""

    myshows_desc = re.search(r'\[Myshows](.+)\[\/Myshows]', show.description, re.DOTALL)
    if myshows_desc:
        description_marked += parse_ner(myshows_desc.group(1), show)

    kinopoisk_desc = re.search(r'\[Kinopoisk](.+)\[\/Kinopoisk]', show.description, re.DOTALL)
    if kinopoisk_desc:
        description_marked += '<hr>'
        description_marked += parse_ner(kinopoisk_desc.group(1), show)

    show.description_marked = description_marked
    show.save()
