# Generated by Django 3.1.7 on 2021-03-16 11:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0019_auto_20210316_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mainapp.person', verbose_name='Личность'),
        ),
        migrations.AlterField(
            model_name='manager',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mainapp.person', verbose_name='Личность'),
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='trainer',
            name='person',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mainapp.person', verbose_name='Личность'),
        ),
    ]
