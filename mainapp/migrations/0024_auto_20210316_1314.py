# Generated by Django 3.1.7 on 2021-03-16 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0023_training'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='training',
            name='group',
        ),
        migrations.AddField(
            model_name='training',
            name='group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='mainapp.group', verbose_name='Группа'),
        ),
    ]
