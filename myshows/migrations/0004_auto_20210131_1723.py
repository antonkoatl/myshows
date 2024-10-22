# Generated by Django 3.1.5 on 2021-01-31 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myshows', '0003_auto_20210127_1459_squashed_0007_auto_20210127_1555'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('name_ru', models.CharField(max_length=200, null=True)),
                ('sex', models.CharField(choices=[('m', 'Мужской'), ('f', 'Женский')], max_length=1)),
                ('growth', models.IntegerField(null=True)),
                ('birthday', models.DateField(null=True)),
                ('death', models.DateField(null=True)),
                ('birthplace', models.CharField(max_length=200, null=True)),
                ('deathplace', models.CharField(max_length=200, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['-published_at']},
        ),
        migrations.CreateModel(
            name='PersonSpouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('divorced', models.BooleanField()),
                ('divorced_reason', models.CharField(max_length=1000, null=True)),
                ('person1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person1_set', to='myshows.person')),
                ('person2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='person2_set', to='myshows.person')),
            ],
        ),
        migrations.CreateModel(
            name='PersonRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('actor', 'Актер'), ('director', 'Режиссер'), ('producer', 'Продюсер'), ('writer', 'Сценарист'), ('operator', 'Оператор'), ('composer', 'Композитор'), ('design', 'Художник'), ('editor', 'Монтажер'), ('voice_dir', 'Режиссёр дубляжа'), ('translator', 'Переводчики')], max_length=10)),
                ('description', models.CharField(max_length=200, null=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshows.person')),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshows.show')),
            ],
        ),
        migrations.CreateModel(
            name='PersonImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='person')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshows.person')),
            ],
        ),
        migrations.CreateModel(
            name='PersonFact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string', models.CharField(max_length=3000)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshows.person')),
            ],
        ),
    ]
