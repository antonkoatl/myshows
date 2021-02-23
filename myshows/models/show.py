import re

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from myshows.models import Country, Genre, Tag, Network
from myshows.models.person import PersonRole


class Show(models.Model):

    class BroadcastStatus(models.TextChoices):
        UNKNOWN = "UKN", _("Неизвестно")
        CANCELED_ENDED = "C/E", _("Отменено/Завершено")
        TBD = "TBD", _("Будет определено")
        RETURNING_SERIES = "AIR", _("Сериал продолжается")
        NEW_SERIES = "NEW", _("Новый сериал")
        IN_DEVELOPMENT = "IND", _("В производстве")

    class ShowTypes(models.TextChoices):
        SHOW = "show", _("Сериал")
        FULL = "full", _("Полнометражный")
        SHORT = "shrt", _("Короткометражный")

    class ShowCategories(models.TextChoices):
        FILM = "film", _("Кино")
        CARTOON = "cart", _("Мультфильм")
        ANIME = "anim", _("Аниме")
        ANIMATION = "anit", _("Анимация")
        THEATRE = "thea", _("Театр")
        TV = "tv", _("ТВ шоу")


    title_original = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200, blank=True)
    slogan = models.CharField(max_length=300, blank=True)
    broadcast_status = models.CharField(max_length=3, default=BroadcastStatus.UNKNOWN, choices=BroadcastStatus.choices)
    seasons_total = models.IntegerField()
    year = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=4, choices=ShowCategories.choices)
    type = models.CharField(max_length=4, choices=ShowTypes.choices)
    country = models.ManyToManyField(Country)
    started = models.DateTimeField()
    ended = models.DateTimeField(null=True)
    runtime_one = models.DurationField()
    runtime_total = models.DurationField(null=True)
    genres = models.ManyToManyField(Genre)
    tags = models.ManyToManyField(Tag)
    network = models.ForeignKey(Network, null=True, on_delete=models.PROTECT)
    age_limit = models.IntegerField(default=0)

    myshows_id = models.IntegerField(null=True)
    myshows_watching = models.IntegerField(null=True)
    myshows_voted = models.IntegerField(null=True)
    myshows_rating = models.FloatField(null=True)

    kinopoisk_id = models.IntegerField(null=True)
    kinopoisk_rating = models.FloatField(null=True)
    kinopoisk_voted = models.IntegerField(null=True)

    tvrage_id = models.IntegerField(null=True)

    imdb_id = models.IntegerField(null=True)
    imdb_rating = models.IntegerField(null=True)
    imdb_voted = models.IntegerField(null=True)

    def get_title_ru(self):
        return self.get_title_static(self.title_ru)

    def directors(self):
        return self.personrole_set.filter(role=PersonRole.RoleType.DIRECTOR)

    @staticmethod
    def get_title_static(title):
        return title.split('::')[0]

    def __str__(self):
        return f'Show[{self.title_original}]'


class Poster(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='poster')
    upload_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    upload_time = models.DateTimeField(auto_now_add=True)
    country = models.ForeignKey(Country, default=1, on_delete=models.SET_DEFAULT)


class Fact(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    string = models.CharField(max_length=3000)

    def __str__(self):
        return f'{self.show}:{self.string[:20]}'


class Review(models.Model):

    class ReviewType(models.TextChoices):
        POSITIVE = "p", _("Позитивный")
        NEGATIVE = "n", _("Негативный")
        NEUTRAL = "u", _("Нейтральный")

    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=ReviewType.choices, null=True)
    date = models.DateTimeField(null=True)
    author = models.CharField(max_length=200)
    title = models.CharField(max_length=1000, null=True)
    description = models.TextField()


class ShowVideo(models.Model):
    class VideoType(models.TextChoices):
        TRAILER = "trailer", _("Трейлер")
        TEASER = "teaser", _("Тизер")
        FRAGMENT = "fragment", _("Фрагмент")

    embed_html = models.TextField()
    type = models.CharField(max_length=10, choices=VideoType.choices)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)


    def get_embed_fit(self):
        html = self.embed_html
        html = re.sub(r'(^<iframe.*width=")(\d+)+("[^>]*>)', lambda x: x[1] + '100%' + x[3], html)
        html = re.sub(r'(^<iframe.*height=")(\d+)+("[^>]*>)', lambda x: x[1] + '100%' + x[3], html)
        return html
