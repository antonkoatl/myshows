import random

from myshows.models import Show, EpisodeImage


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

    shows_with_images = list(shows.filter(season__episode__episodeimage__isnull=False).distinct().values_list('pk', 'title_ru'))
    shows = random.sample(shows_with_images, 4)
    correct = random.choice(shows)

    variants = [Show.get_title_static(x[1]) for x in shows]

    return {
        'image_url': EpisodeImage.objects.filter(episode__season__show=correct[0]).order_by('?').first().image.url,
        'text_variants': variants,
        'text_correct': correct[1],
        'correct_answer_num': shows.index(correct)
    }
