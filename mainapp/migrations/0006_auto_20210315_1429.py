# Generated by Django 3.1.7 on 2021-03-15 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_auto_20210315_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='Galery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=128, verbose_name='Заголовок события в галерее')),
                ('description', models.TextField(blank=True, max_length=512, null=True, verbose_name='Описание галереи')),
                ('event_photo', models.ImageField(upload_to='', verbose_name='Фото галереи')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=256, verbose_name='Заголовок новости')),
                ('news_photo', models.ImageField(upload_to='', verbose_name='Изображение новости')),
                ('description', models.TextField(max_length=4096, verbose_name='Описание')),
            ],
        ),
        migrations.AlterField(
            model_name='pack',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Цена'),
        ),
        migrations.CreateModel(
            name='PhotoInGalery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_photo', models.ImageField(upload_to='', verbose_name='Изображение события')),
                ('galery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.galery', verbose_name='Галерея')),
            ],
        ),
    ]
