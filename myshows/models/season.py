from django.db import models

from myshows.models import Show


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
