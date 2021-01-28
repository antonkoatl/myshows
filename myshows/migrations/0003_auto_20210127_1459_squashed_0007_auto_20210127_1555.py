# Generated by Django 3.1.5 on 2021-01-28 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('myshows', '0003_auto_20210127_1459'), ('myshows', '0004_auto_20210127_1530'), ('myshows', '0005_auto_20210127_1534'), ('myshows', '0006_auto_20210127_1546'), ('myshows', '0007_auto_20210127_1555')]

    dependencies = [
        ('myshows', '0002_poster_country_squashed_0009_auto_20210127_0018'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='episode',
            options={'ordering': ['-number']},
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('p', 'Позитивный'), ('n', 'Негативный'), ('u', 'Нейтральный')], max_length=1, null=True)),
                ('date', models.DateTimeField(null=True)),
                ('author', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=1000, null=True)),
                ('description', models.TextField()),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshows.show')),
            ],
        ),
        migrations.CreateModel(
            name='EpisodeComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=200)),
                ('comment', models.TextField(max_length=5000)),
                ('created_at', models.DateTimeField()),
                ('rating', models.IntegerField()),
                ('dost_positive', models.FloatField()),
                ('dost_neutral', models.FloatField()),
                ('dost_negative', models.FloatField()),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshows.episode')),
            ],
        ),
    ]
