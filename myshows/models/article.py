from django.contrib.auth.models import User
from django.db import models
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
    content_marked = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    video = models.CharField(max_length=5000, null=True)
    category = models.CharField(max_length=20, choices=ArticleCategories.choices)
    tags = models.CharField(max_length=1000)
    source = models.CharField(max_length=1000)

    def __str__(self):
        return self.title


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
