import re

import celery
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from myshows.models import Country, Genre, Tag, Network
from myshows.models.person import PersonRole


class Show(models.Model):
    class Meta:
        ordering = ['-myshows_watching']

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
    ended = models.DateTimeField(null=True, blank=True)
    runtime_one = models.DurationField()
    runtime_total = models.DurationField(null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
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

    entity_occurrences = GenericRelation('NamedEntityOccurrence')

    def get_title_ru(self):
        return self.get_title_static(self.title_ru)

    def directors(self):
        return self.personrole_set.filter(role=PersonRole.RoleType.DIRECTOR).select_related('person')

    def get_poster(self):
        if len(self.poster_set.all()) > 0:
            return self.poster_set.all()[0].image.url  # Can't use first() here because it clears cached queryset for prefetch_related
        else:
            return static('poster_placeholder.jpg')

    @staticmethod
    def get_title_static(title):
        return title.split('::')[0]

    def __str__(self):
        return f'Show[{self.title_original}]'


@receiver(pre_save, sender=Show)
def update_description_markup_pre(sender, instance: Show, **kwargs):
    instance.update_description = False
    if instance.id is None:
        instance.update_description = True
    else:
        previous = sender.objects.get(id=instance.id)
        if previous.description != instance.description:  # field will be updated
            instance.update_description = True


@receiver(post_save, sender=Show)
def update_content_markup_post(sender, instance: Show, **kwargs):
    if instance.update_description:
        transaction.on_commit(
            lambda:
            celery.current_app.send_task('myshows.tasks.process_show_description', (instance.id,)))


class Poster(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='poster')
    upload_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    upload_time = models.DateTimeField(auto_now_add=True)
    country = models.ForeignKey(Country, default=1, on_delete=models.SET_DEFAULT)


class Fact(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    string = models.CharField(max_length=3000)
    entity_occurrences = GenericRelation('NamedEntityOccurrence')

    def __str__(self):
        return f'{self.show}:{self.string[:20]}'


@receiver(pre_save, sender=Fact)
def update_content_markup_fact_pre(sender, instance: Fact, **kwargs):
    instance.update_description = False
    if instance.id is None:
        instance.update_description = True
    else:
        previous = sender.objects.get(id=instance.id)
        if previous.string != instance.string:  # field will be updated
            instance.update_description = True


@receiver(post_save, sender=Fact)
def update_content_markup_fact_post(sender, instance: Fact, **kwargs):
    if instance.update_description:
        transaction.on_commit(
            lambda: celery.current_app.send_task('myshows.tasks.process_fact_description', (instance.id,)))


class Review(models.Model):
    class Meta:
        ordering = ['-date', ]

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
    entity_occurrences = GenericRelation('NamedEntityOccurrence')

    def __str__(self):
        return self.title + " " + str(self.show)


@receiver(pre_save, sender=Review)
def update_content_markup_review_pre(sender, instance: Review, **kwargs):
    instance.update_description = False
    if instance.id is None:
        instance.update_description = True
    else:
        previous = sender.objects.get(id=instance.id)
        if previous.description != instance.description:  # field will be updated
            instance.update_description = True


@receiver(post_save, sender=Review)
def update_content_markup_review_post(sender, instance: Review, **kwargs):
    if instance.update_description:
        transaction.on_commit(
            lambda: celery.current_app.send_task('myshows.tasks.process_review_description', (instance.id,)))


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
