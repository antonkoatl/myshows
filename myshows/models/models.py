from django.db import models
from django.utils.translation import gettext_lazy as _


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
