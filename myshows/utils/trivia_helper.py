import random

from django.db.models import Count

from myshows.models.person import PersonRole
from myshows.models.episode import EpisodeImage
from myshows.models.show import Show


def get_new_question(mode):
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

    question_type = random.randrange(2)
    question = {'type': question_type}

    if question_type == 0:
        shows_with_images = list(shows.filter(season__episode__episodeimage__isnull=False).distinct().values_list('pk', 'title_ru'))
        question_shows = random.sample(shows_with_images, 4)
        correct = random.choice(question_shows)
        variants = [Show.get_title_static(x[1]) for x in question_shows]

        question['image_url'] = EpisodeImage.objects.filter(episode__season__show=correct[0]).order_by('?').first().image.url
        question['text_variants'] = variants
        question['correct_answer_num'] = question_shows.index(correct)
    elif question_type == 1:
        shows_with_actors = list(shows.filter(personrole__role=PersonRole.RoleType.ACTOR,
                                              personrole__person__personimage__isnull=False
                                              ).annotate(actors_count=Count('personrole')
                                                         ).values('actors_count', 'title_ru', 'pk').filter(actors_count__gte=5))

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

    return question
