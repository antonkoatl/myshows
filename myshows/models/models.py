from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Country(models.TextChoices):
    UNKNOWN = "UN", _("Неизвестно")
    GREAT_BRITAIN = "UK", _("Великобритания")
    USA = "US", _("США")
    JAPAN = "JP", _("Япония")
    CANADA = "CA", _("Канада")
    NORWAY = "NO", _("Норвегия")
    RUSSIA = "RU", _("Россия")
    ITALY = "IT", _("Италия")
    AUSTRALIA = "AU", _("Австралия")
    USSR = "SU", _("СССР")
    FRANCE = "FR", _("Франция")
    SWEDEN = "SE", _("Швеция")
    UKRAINE = "UA", _("Украина")
    ARGENTINA = "AR", _("Аргентина")
    KOREA = "KR", _("Южная Корея")
    LATVIA = "LV", _("Латвия")
    TURKEY = "TR", _("Турция")
    GERMANY = "DE", _("Германия")
    BRASIL = "BR", _("Бразилия")


class Network(models.Model):
    title = models.CharField(max_length=200)
    country = models.CharField(max_length=2, choices=Country.choices, default=Country.UNKNOWN)

    def __str__(self):
        return f"{self.title} - {self.country}"


class Genre(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return str(self.title)


class Tag(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return str(self.title)


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
    broadcast_status = models.CharField(max_length=3, default=BroadcastStatus.UNKNOWN, choices=BroadcastStatus.choices)
    seasons_total = models.IntegerField()
    year = models.IntegerField()
    description = models.TextField()
    category = models.CharField(max_length=4, choices=ShowCategories.choices)
    type = models.CharField(max_length=4, choices=ShowTypes.choices)
    country = models.CharField(max_length=200, default=Country.UNKNOWN.value)
    started = models.DateField()
    ended = models.DateField(null=True)
    runtime_one = models.DurationField()
    runtime_total = models.DurationField(null=True)
    runtime_total_str = models.CharField(max_length=200)
    genres = models.ManyToManyField(Genre)
    tags = models.ManyToManyField(Tag)
    network = models.ForeignKey(Network, null=True, on_delete=models.PROTECT)

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


    def __str__(self):
        return f'Show[{self.title_original}]'


class Poster(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='poster')
    upload_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    upload_time = models.DateTimeField(auto_now_add=True)


class Article(models.Model):
    class ArticleCategories(models.TextChoices):
        TRAILER = "trailer", _("Трейлер")
        ANNOUNCE = "anonsy", _("Анонс")
        ARTICLE = "articles", _("Статья")
        BLOG = "blog", _("Блог")

    title = models.CharField(max_length=1000)
    foreword = models.CharField(max_length=1000)
    content = models.TextField()
    published_at = models.DateTimeField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    video = models.CharField(max_length=5000, null=True)
    category = models.CharField(max_length=20, choices=ArticleCategories.choices)
    tags = models.CharField(max_length=1000)
    source = models.CharField(max_length=1000)


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
