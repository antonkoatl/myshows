import random
import re

from django.db.models import Count

from myshows.models.person import PersonRole
from myshows.models.episode import EpisodeImage
from myshows.models.show import Show


def get_new_question(mode='shows'):
    """
    Function to generate trivia question

    Parameters
    ----------
    mode : str
        Trivia mode. (shows, cartoon, anime, russia, america)

    Returns
    -------
    question : dict
        Generated question. Possible variants:
            type = 0
            image_url : str, url of image file
            text_variants : list(str), list of text variants for question
            correct_answer_num : int, index of correct answer

            type = 1
            image_url : list(str), list of urls of image files
            text_variants : list(str), list of text variants for question
            correct_answer_num : int, index of correct answer

            type = 2
            question_text : str, text of question
            text_variants : list(str), list of text variants for question
            correct_answer_num : int, index of correct answer
    """

    shows = Show.objects.all()

    if mode == 'shows':
        shows = shows.filter(category=Show.ShowCategories.FILM)
    elif mode == 'cartoon':
        shows = shows.filter(category=Show.ShowCategories.CARTOON)
    elif mode == 'anime':
        shows = shows.filter(category=Show.ShowCategories.ANIME)
    elif mode == 'russia':
        shows = shows.filter(country__name_short='RU')
    elif mode == 'america':
        shows = shows.filter(country__name_short='US')

    question_type = random.randrange(3)
    question = {'type': question_type}

    if question_type == 0:
        # Get shows with episode images
        shows_with_images = list(shows.filter(season__episode__episodeimage__isnull=False).distinct().values_list('pk', 'title_ru'))
        question_shows = random.sample(shows_with_images, 4)
        correct = random.choice(question_shows)
        variants = [Show.get_title_static(x[1]) for x in question_shows]

        question['image_url'] = EpisodeImage.objects.filter(episode__season__show=correct[0]).order_by('?').first().image.url
        question['text_variants'] = variants
        question['correct_answer_num'] = question_shows.index(correct)

    elif question_type == 1:
        # Get show with at least 5 actors with image
        shows_with_actors = list(shows.filter(
            personrole__role=PersonRole.RoleType.ACTOR, personrole__person__personimage__isnull=False
        ).annotate(actors_count=Count('personrole')).values('actors_count', 'title_ru', 'pk').filter(actors_count__gte=5))

        question_shows = random.sample(shows_with_actors, 4)
        correct = random.choice(question_shows)
        variants = [Show.get_title_static(x['title_ru']) for x in question_shows]

        question['image_url'] = []

        for person_role in Show.objects.get(pk=correct['pk']).personrole_set.filter(
                role=PersonRole.RoleType.ACTOR, person__personimage__isnull=False).select_related('person')[:5]:
            image_url = person_role.person.personimage_set.first().image.url
            question['image_url'].append(image_url)

        question['text_variants'] = variants
        question['correct_answer_num'] = question_shows.index(correct)

    elif question_type == 2:
        shows = list(shows.values_list('id', flat=True))

        question_shows = list(Show.objects.filter(id__in=random.sample(shows, 4)))
        correct = random.choice(question_shows)
        variants = [x.get_title_ru() for x in question_shows]

        description_marked = correct.description

        for occurrence in correct.entity_occurrences.select_related('named_entity'):
            description_marked = description_marked[:occurrence.position_start] + \
                                 f'''<span class="badge bg-light text-dark">{occurrence.named_entity.get_type_display()}</span>''' + description_marked[occurrence.position_end:]

        description = ''
        myshows_desc = re.search(r'\[Myshows](.+)\[\/Myshows]', description_marked, re.DOTALL)
        kinopoisk_desc = re.search(r'\[Kinopoisk](.+)\[\/Kinopoisk]', description_marked, re.DOTALL)
        if kinopoisk_desc:
            description = '<p>' + myshows_desc.group(1) + '</p>'
        elif myshows_desc:
            description = '<p>' + kinopoisk_desc.group(1) + '</p>'

        question['question_text'] = description
        question['text_variants'] = variants
        question['correct_answer_num'] = question_shows.index(correct)

    return question
