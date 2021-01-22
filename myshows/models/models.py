from django.contrib.auth.models import User
from django.db import models


class Show(models.Model):
    name_original = models.CharField(max_length=200)
    description = models.TextField()


class Poster(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='poster')
    upload_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    upload_time = models.DateTimeField(auto_now_add=True)
