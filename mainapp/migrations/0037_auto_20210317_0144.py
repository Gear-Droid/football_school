# Generated by Django 3.1.7 on 2021-03-17 01:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0036_auto_20210317_0023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='galery',
            old_name='event_photo',
            new_name='galery_photo',
        ),
    ]
