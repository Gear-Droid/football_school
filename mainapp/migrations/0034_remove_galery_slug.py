# Generated by Django 3.1.7 on 2021-03-17 00:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0033_galery_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='galery',
            name='slug',
        ),
    ]
