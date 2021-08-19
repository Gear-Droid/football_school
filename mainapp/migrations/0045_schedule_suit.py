# Generated by Django 3.1.7 on 2021-08-19 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0044_schedule_day_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='suit',
            field=models.IntegerField(choices=[(1, 'Diamond'), (2, 'Spade'), (3, 'Heart'), (4, 'Club')], default=1),
            preserve_default=False,
        ),
    ]
