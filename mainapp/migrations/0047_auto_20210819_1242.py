# Generated by Django 3.1.7 on 2021-08-19 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0046_auto_20210819_1237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='suit',
            new_name='train_day',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='day_number',
        ),
    ]
