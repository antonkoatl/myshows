import re

import celery
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


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
    video = models.CharField(max_length=5000, null=True, blank=True)
    category = models.CharField(max_length=20, choices=ArticleCategories.choices)
    tags = models.CharField(max_length=1000)
    source = models.CharField(max_length=1000)
    entity_occurrences = GenericRelation('NamedEntityOccurrence')

    def get_embed_fit_video(self):
        html = self.video
        html = re.sub(r'(^<iframe.*width=")(\d+)+("[^>]*>)', lambda x: x[1] + '300' + x[3], html)
        html = re.sub(r'(^<iframe.*height=")(\d+)+("[^>]*>)', lambda x: x[1] + '100%' + x[3], html)
        return html

    def __str__(self):
        return self.title


@receiver(pre_save, sender=Article)
def update_content_markup_pre(sender, instance: Article, **kwargs):
    instance.update_description = False
    if instance.id is None:
        instance.update_description = True
    else:
        previous = sender.objects.get(id=instance.id)
        if previous.content != instance.content:  # field will be updated
            instance.update_description = True


@receiver(post_save, sender=Article)
def update_content_markup_post(sender, instance: Article, **kwargs):
    if instance.update_description:
        transaction.on_commit(
            lambda: celery.current_app.send_task('myshows.tasks.process_article_description', (instance.id,)))



class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
