import celery
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.db.models import Q, OuterRef
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _


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

    def get_spouses(self):
        return Person.objects.filter(
            Q(id__in=self.person1_set.values_list('person2', flat=True)) |
            Q(id__in=self.person2_set.values_list('person1', flat=True))
        ).annotate(
            divorced=PersonSpouse.objects.filter(
                Q(person1=self, person2=OuterRef('id')) | Q(person2=self, person1=OuterRef('id'))
            ).values_list('divorced', flat=True)
        )

    def get_poster(self):
        if len(self.personimage_set.all()) > 0:
            return self.personimage_set.all()[0].image.url  # Can't use first() here because it clears cached queryset for prefetch_related
        else:
            return static('poster_placeholder.jpg')

    def __str__(self):
        return f'{self.get_name()}'


class PersonImage(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='person')


class PersonFact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    string = models.CharField(max_length=3000)
    entity_occurrences = GenericRelation('NamedEntityOccurrence')

    def __str__(self):
        return f'{self.person}:{self.string[:20]}'


@receiver(pre_save, sender=PersonFact)
def update_content_markup_fact_pre(sender, instance: PersonFact, **kwargs):
    instance.update_description = False
    if instance.id is None:
        instance.update_description = True
    else:
        previous = sender.objects.get(id=instance.id)
        if previous.string != instance.string:  # field will be updated
            instance.update_description = True


@receiver(post_save, sender=PersonFact)
def update_content_markup_fact_post(sender, instance: PersonFact, **kwargs):
    if instance.update_description:
        transaction.on_commit(
            lambda: celery.current_app.send_task('myshows.tasks.process_person_fact_description', (instance.id,)))


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
    show = models.ForeignKey('myshows.Show', on_delete=models.CASCADE)
    description = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f'{self.person} {self.role} {self.show}'
