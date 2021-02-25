from django.contrib.postgres.operations import TrigramExtension

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('myshows', '0007_showvideo'),
    ]

    operations = [
        TrigramExtension(),
    ]
