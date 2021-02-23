# Generated by Django 3.1.5 on 2021-02-01 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myshows', '0005_person_animated_poster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personrole',
            name='role',
            field=models.CharField(choices=[('actor', 'Актер'), ('director', 'Режиссер'), ('producer', 'Продюсер'), ('writer', 'Сценарист'), ('operator', 'Оператор'), ('composer', 'Композитор'), ('design', 'Художник'), ('editor', 'Монтажер'), ('voice_dir', 'Режиссёр дубляжа'), ('translator', 'Переводчики'), ('producersu', 'Директор фильма')], max_length=10),
        ),
    ]