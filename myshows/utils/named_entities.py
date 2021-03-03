from html.parser import HTMLParser
from itertools import chain

import spacy
from django.contrib.contenttypes.models import ContentType

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
    """Merge multiple results"""
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

    return ents


def get_lemma(entity):
    """Returns lemma or text of entity"""
    if len(entity.lemma_) > 0:
        return entity.lemma_.lower().strip()
    else:
        return entity.text.lower().strip()


def parse_ner_text(text, content_object, offset):
    """Parse simple text for Named Entities"""
    doc_ru = nlp_ru(text)
    doc_en = nlp_en(text)
    doc_xx = nlp_xx(text)

    ents_all = merge_ents(
        doc_ru.ents,
        filter(lambda x: x.label_ in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'CARDINAL'], doc_en.ents),
        filter(lambda x: x.label_ == 'MISC', doc_xx.ents))

    ents_all.sort(key=lambda x: x.start_char)

    for entity in ents_all:
        process_founded_entity(entity, content_object, offset)


def process_founded_entity(entity, content_object, offset):
    """Add occurrence to db if not exist"""
    entity_db = NamedEntity.objects.filter(lemma__lemma=get_lemma(entity)).first()

    if not entity_db:
        entity_db = NamedEntity(name=entity.text.strip(),
                                type=NamedEntity.Type(entity_types.get(entity.label_, entity.label_)))
        entity_db.save()
        entity_db.lemma_set.create(lemma=get_lemma(entity))

    occurrence_db = NamedEntityOccurrence.objects.filter(
        content_type=ContentType.objects.get_for_model(content_object),
        object_id=content_object.id,
        position_start=offset+entity.start_char,
        position_end=offset+entity.end_char
    )

    if not occurrence_db.exists():
        occurrence_db = NamedEntityOccurrence(
            named_entity=entity_db,
            content_object=content_object,
            position_start=offset+entity.start_char,
            position_end=offset+entity.end_char
        )
        occurrence_db.save()

    return entity_db, occurrence_db


def parse_html_text(html_text, content_object, offset=0):
    """Function to parse HTML for Named Entities"""
    lines = html_text.split('\n')

    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            pass

        def handle_endtag(self, tag):
            pass

        def handle_data(self, data):
            if self.lasttag == 'script':
                return
            pos = offset + self.getpos()[1]
            for i in range(self.getpos()[0] - 1):
                pos += len(lines[i]) + 1

            parse_ner_text(data, content_object, pos)

    parser = MyHTMLParser(convert_charrefs=False)
    parser.feed(html_text)
