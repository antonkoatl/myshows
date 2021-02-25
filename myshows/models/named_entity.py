from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class NamedEntity(models.Model):
    class Meta:
        verbose_name = _(u"Named Entity")
        verbose_name_plural = _(u"Named Entities")

    class Type(models.TextChoices):
        PERSON = "PER", _("Персонаж")
        LOCATION = "LOC", _("Место")
        ORGANIZATION = "ORG", _("Организация")
        PERCENT = "PRC", _("Процент")
        DATE = "DAT", _("Дата")
        TIME = "TIM", _("Время")
        CARDINAL = "CAR", _("Число")  # Numerals that do not fall under another type
        MISC = "MIS", _("Разное")

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=3, choices=Type.choices)

    def __str__(self):
        return f'{self.name} {self.type}'


class Lemma(models.Model):
    lemma = models.CharField(max_length=200)
    named_entity = models.ForeignKey(NamedEntity, on_delete=models.CASCADE)


class NamedEntityOccurrence(models.Model):
    named_entity = models.ForeignKey(NamedEntity, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.named_entity} {self.content_object}'
