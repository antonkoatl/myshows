from django.db import models
from django.db.models import Avg

from myshows.models import Season
from myshows.utils.sentimental import dostoevsky_analyze


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
        if hasattr(self, 'temp_avg'):
            return self.temp_avg
        else:
            temp_avg = self.episodecomment_set.aggregate(Avg('dost_positive'), Avg('dost_neutral'), Avg('dost_negative'))
            temp_sum = sum(filter(None, temp_avg.values()))
            for k in temp_avg:
                if temp_avg[k] is not None:
                    temp_avg[k] = temp_avg[k] / temp_sum
                else:
                    temp_avg[k] = 0
            self.temp_avg = temp_avg
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