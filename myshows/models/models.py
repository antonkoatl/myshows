from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _

from myshows.utils.sentimental import dostoevsky_analyze


class Country(models.Model):
    name_short = models.CharField(max_length=2)
    name = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name_ru)

    class Meta:
        verbose_name = _(u"Country")
        verbose_name_plural = _(u"Countries")


class Network(models.Model):
    title = models.CharField(max_length=200)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

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


class Article(models.Model):
    class Meta:
        ordering = ['-published_at', ]

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


class Season(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    number = models.IntegerField()
    episodes_count = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    description = models.TextField()
    trailer = models.TextField()

    def __str__(self):
        return f'Season[{self.show}:{self.number}]'

    class Meta:
        ordering = ['-number', ]


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    title_ru = models.CharField(max_length=200, null=True)
    number = models.IntegerField()
    air_date = models.DateTimeField(null=True)
    is_special = models.BooleanField()
    synopsis = models.CharField(max_length=2000, null=True)

    def __str__(self):
        return f'Episode[{self.season.show.get_title_ru()} : {self.season.number} : {self.number} {self.get_title()}]'

    class Meta:
        ordering = ['-number', ]

    def get_title(self):
        if self.title_ru is not None: return self.title_ru
        elif self.title is not None: return self.title
        else: return ""

    def get_comments_temperature(self):
        temp_avg = self.episodecomment_set.aggregate(Avg('dost_positive'), Avg('dost_neutral'), Avg('dost_negative'))
        temp_sum = sum(filter(None, temp_avg.values()))
        for k in temp_avg:
            if temp_avg[k] is not  None:
                temp_avg[k] = temp_avg[k] / temp_sum
            else:
                temp_avg[k] = ''
        return temp_avg


class EpisodeImage(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='episode')


class EpisodeComment(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=200)
    comment = models.TextField(max_length=5000)
    created_at = models.DateTimeField()
    rating = models.IntegerField()
    dost_positive = models.FloatField()
    dost_neutral = models.FloatField()
    dost_negative = models.FloatField()

    def save(self, *args, **kwargs):
        results = dostoevsky_analyze(self.comment)
        self.dost_positive = results['positive']
        self.dost_neutral = results['neutral']
        self.dost_negative = results['negative']
        super(EpisodeComment, self).save(*args, **kwargs)


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


class Person(models.Model):

    class Gender(models.TextChoices):
        MALE = "m", _("Мужской")
        FEMALE = "f", _("Женский")

    name = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200, null=True)
    sex = models.CharField(max_length=1, choices=Gender.choices)
    growth = models.IntegerField(null=True)
    birthday = models.DateField(null=True)
    death = models.DateField(null=True)
    birthplace = models.CharField(max_length=200, null=True)
    deathplace = models.CharField(max_length=200, null=True)
    animated_poster = models.FileField(upload_to='animated_posters/', null=True)

    def get_name(self):
        if self.name_ru is not None:
            return self.name_ru
        else:
            return self.name

    def __str__(self):
        return f'{self.get_name()}'


class PersonImage(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='person')


class PersonFact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    string = models.CharField(max_length=3000)

    def __str__(self):
        return f'{self.person}:{self.string[:20]}'


class PersonSpouse(models.Model):
    person1 = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person1_set')
    person2 = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person2_set')
    divorced = models.BooleanField()
    divorced_reason = models.CharField(max_length=1000, null=True)


class PersonRole(models.Model):

    class RoleType(models.TextChoices):
        ACTOR = "actor", _("Актер")
        DIRECTOR = "director", _("Режиссер")
        PRODUCER = "producer", _("Продюсер")
        WRITER = "writer", _("Сценарист")
        OPERATOR = "operator", _("Оператор")
        COMPOSER = "composer", _("Композитор")
        DESIGN = "design", _("Художник")
        EDITOR = "editor", _("Монтажер")
        VOICE_DIRECTOR = "voice_dir", _("Режиссёр дубляжа")
        TRANSLATOR = "translator", _("Переводчики")
        PRODUCER_USSR = "producersu", _("Директор фильма")


    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=RoleType.choices)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.person} {self.role} {self.show}'
