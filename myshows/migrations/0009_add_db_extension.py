from django.contrib.postgres.operations import TrigramExtension

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('myshows', '0008_auto_20210225_1847'),
    ]

    operations = [
        TrigramExtension(),
    ]
