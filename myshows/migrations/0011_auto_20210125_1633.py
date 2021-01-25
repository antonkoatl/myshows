# Generated by Django 3.1.5 on 2021-01-25 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myshows', '0010_remove_show_runtime_total_str'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='season',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='show',
            name='ended',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='started',
            field=models.DateTimeField(),
        ),
    ]
