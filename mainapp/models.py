from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.utils.html import format_html


User = get_user_model()


# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   User
#
# Стандартный Django User
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   PreRegisterUserEmail
#
# Хранит email и id для формирования приглашений
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Galery
#
# Хранит PhotoInGalery, имеет: заголовок, описание и одну фото
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
# PhotoInGalery
#
# Событие для галереи с заголовком, описанием, фотографиями
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   News
#
# Новостное событие с заголовком, описанием, фото
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Person
#
# Ссылается на User и дополняет его атрибутом phone
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Child
#
# fk на Person с доп. полями
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Trainer
#
# fk на Person с доп. полями
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Manager
#
# fk на Person
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Pack
#
# Набор тренировок (цена, тренировки, заморозки)
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   AgeCategory
#
# Возрастные категории: мин и макс возраст
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Group
#
# Ссылается на: Тренеров, Возрастную группу, Отделение
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Department
#
# Отделение (имеет адрес, название, тренеров, фото и пакеты)
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Schedule
#
# Расписание (день, время начала, конца, отделение и группа)
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Training
#
# Информация о тренировке
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #
#   Payment
#
# Информация об оплате
# <<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>> #


class PreRegisterUserEmail(models.Model):

    class Meta:
        verbose_name_plural = 'Предрегистрационные почтовые адреса'

    email = models.EmailField(
        verbose_name='email с приглашением',
        max_length=254, null=False, blank=False, unique=True
    )

    def __str__(self):
        return f"{self.email}"


class Galery(models.Model):

    class Meta:
        verbose_name_plural = 'Галереи'

    header = models.CharField(
        max_length=128,
        verbose_name='Заголовок события в галерее'
    )
    description = models.TextField(
        max_length=512,
        verbose_name='Описание галереи', null=True, blank=True
    )
    galery_photo = models.ImageField(verbose_name='Фото галереи')
    slug = models.SlugField(unique=True)

    def get_absolute_url(self):
        return reverse('galery_detail', kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return f"{self.pk}. Галерея: ({self.header})"


class PhotoInGalery(models.Model):

    class Meta:
        verbose_name_plural = 'Фотографии в галерее'

    galery = models.ForeignKey(
        Galery, verbose_name='Галерея', on_delete=models.CASCADE
    )
    event_photo = models.ImageField(verbose_name='Изображение события')

    def __str__(self):
        return f"{self.galery.header}: Фото-{self.pk}"


class News(models.Model):

    class Meta:
        verbose_name_plural = 'Новости'

    header = models.CharField(
        max_length=255, verbose_name='Заголовок новости'
    )
    news_photo = models.ImageField(
        verbose_name='Изображение новости', null=True, blank=True
    )
    description = models.TextField(
        max_length=4096, verbose_name='Описание'
    )

    def __str__(self):
        return f"{self.pk}. {self.header}"


class Person(models.Model):

    class Meta:
        verbose_name_plural = 'Люди'

    user = models.OneToOneField(
        User, verbose_name='Пользователь', on_delete=models.CASCADE
    )
    phone = models.CharField(
        max_length=20, verbose_name='Номер телефона'
    )

    def __str__(self):
        
        return "{}. {} ({} {})".format(
            self.user.pk,
            self.user.username,
            self.user.first_name,
            self.user.last_name
        )


class Child(models.Model):

    class Meta:
        verbose_name_plural = 'Дети'

    person = models.OneToOneField(
        Person, verbose_name='Личность', on_delete=models.CASCADE
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения', null=True, blank=True
    )
    trainings_count = models.PositiveIntegerField(
        default=0, verbose_name='Кол-во тренировок'
    )
    trainings_freeze_count = models.PositiveIntegerField(
        default=0, verbose_name='Кол-во заморозок'
    )

    def groups(self):
        return list(Group.objects.filter(children=self))
    groups.short_description = "Группы"

    def phone(self):
        return self.person.phone
    phone.short_description = "Телефон"

    def email(self):
        return self.person.user.email
    email.short_description = "Адрес электронной почты"

    def __str__(self):
        return f"Ребенок: ({self.person})"


class Trainer(models.Model):

    class Meta:
        verbose_name_plural = 'Тренеры'

    person = models.OneToOneField(
        Person, verbose_name='Личность', on_delete=models.CASCADE
    )
    image = models.ImageField(
        verbose_name='Изображение', null=True, blank=True
    )

    def __str__(self):
        return f"Тренер: ({self.person})"


class Manager(models.Model):

    class Meta:
        verbose_name_plural = 'Менеджеры'

    person = models.OneToOneField(
        Person, verbose_name='Личность', on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Менеджер: ({self.person})"


class Pack(models.Model):

    class Meta:
        verbose_name_plural = 'Пакеты тренировок'
        unique_together = (('trainings_count', 'trainings_freeze_count'),)

    price = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name='Цена'
    )
    trainings_count = models.PositiveIntegerField(
        default=0, verbose_name='Кол-во тренировок'
    )
    trainings_freeze_count = models.PositiveIntegerField(
        default=0, verbose_name='Кол-во заморозок'
    )

    def __str__(self):
        return "{}. Пакет: (Цена {} | Тренировок {} | Заморозок {})".format(
            self.pk, self.price, self.trainings_count, self.trainings_freeze_count
        )


class AgeCategory(models.Model):

    class Meta:
        verbose_name_plural = 'Категории возрастов'
        unique_together = (('min_age', 'max_age'),)

    min_age = models.PositiveIntegerField(
        verbose_name='Минимальный возраст'
    )
    max_age = models.PositiveIntegerField(
        verbose_name='Максимальный возраст'
    )

    def __str__(self):
        return "{} - {}".format(
            self.min_age, self.max_age
        )


class Group(models.Model):

    class Meta:
        verbose_name_plural = 'Группы'

    name = models.CharField(
        max_length=255, verbose_name='Название группы', unique=True
    )
    age_category = models.ForeignKey(
        AgeCategory, verbose_name='Возрастная группа', on_delete=models.CASCADE
    )
    trainers = models.ManyToManyField(
        Trainer, verbose_name='Тренеры группы', blank=True
    )
    children = models.ManyToManyField(
        Child, verbose_name='Дети группы', blank=True
    )

    def departments(self):
        schedules_with_group = Schedule.objects.filter(groups=self)
        uniques = set()
        for schedule in schedules_with_group:
            dep = schedule.department.name
            uniques.add(dep)
        return list(uniques)
    departments.short_description = "Отделения"

    def __str__(self):
        return "{}".format(self.name)


class Department(models.Model):

    class Meta:
        verbose_name_plural = 'Отделения'

    name = models.CharField(max_length=255, verbose_name='Название отделения', unique=True)
    address = models.CharField(max_length=255, verbose_name='Адрес отделения')
    photo = models.ImageField(
        verbose_name='Изображение отделения', null=True, blank=True
    )
    packs = models.ManyToManyField(
        Pack, verbose_name='Пакеты отделения', blank=True
    )
    trainers = models.ManyToManyField(
        Trainer, verbose_name='Тренеры отделения', blank=True
    )
    groups = models.ManyToManyField(
        Group, verbose_name='Группы отделения', blank=True
    )

    def __str__(self):
        return "{}".format(self.name)


class Schedule(models.Model):

    class Meta:
        verbose_name_plural = 'Расписание'
        unique_together = (
            (
                'train_day',
                'department',
                'starttime',
                'endtime',
            ), 
        )

    class Day(models.IntegerChoices):
        MONDAY = 1
        TUESDAY = 2
        WEDNESDAY = 3
        THURSDAY = 4
        FRIDAY = 5
        SATURDAY = 6
        SUNDAY = 7

    train_day = models.IntegerField(
        verbose_name='День тренировки',
        choices=Day.choices,
    )
    groups = models.ManyToManyField(
        Group, verbose_name='Группы'
    )
    department = models.ForeignKey(
        Department, verbose_name='Отделение', on_delete=models.CASCADE
    )
    starttime = models.TimeField(verbose_name='Время начала тренировки')
    endtime = models.TimeField(verbose_name='Время окончания тренировки')

    DAY_REPRESENTATION = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    }

    def __str__(self):
        return '{} - {} ({}-{})'.format(
            self.DAY_REPRESENTATION[self.train_day],
            self.department.name,
            self.starttime,
            self.endtime
        )


class Training(models.Model):

    class Meta:
        verbose_name_plural = 'Тренировки'
        unique_together = (
            (
                'date',
                'department',
                'group',
                'starttime',
                'endtime',
            ), 
        )

    STATUS_NOT_STATED = 'not_stated'
    STATUS_DONE = 'done'
    STATUS_NOT_TOOK_PLACE = 'not_took_place'

    STATUS_CHOICES = (
        (STATUS_NOT_STATED, 'Неопределенный'),
        (STATUS_DONE, 'Выполнена'),
        (STATUS_NOT_TOOK_PLACE, 'Не состоялась'),
    )

    date = models.DateField(verbose_name='Дата тренировки')
    department = models.ForeignKey(
        Department, verbose_name='Отделение', on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group, verbose_name='Группа', on_delete=models.CASCADE,
    )
    starttime = models.TimeField(verbose_name='Начало')
    endtime = models.TimeField(verbose_name='Конец')
    children = models.ManyToManyField(
        Child, verbose_name='Дети присутствовавшие на тренировке', default=None, blank=True
    )
    status = models.CharField(
        max_length=14,
        verbose_name='Состояние',
        choices=STATUS_CHOICES,
        default=STATUS_NOT_STATED
    )
    reserve_trainers = models.ManyToManyField(
        Trainer, verbose_name='Заменяющие тренеры', default=None, blank=True
    )

    STATUS_CASES = {
        STATUS_NOT_STATED: '',
        STATUS_DONE: '<span style="color:white; background-color: green;"><b>{0}</b></span>',
        STATUS_NOT_TOOK_PLACE: '<span style="color:white; background-color: red;"><b>{0}</b></span>',
    }
    STATUS_REPRESENTATION = {
        STATUS_NOT_STATED: 'Неопределенный',
        STATUS_DONE: 'Выполнена',
        STATUS_NOT_TOOK_PLACE: 'Не состоялась',
    }
    def colored_status(self):
        if self.status == 'not_stated':
            return self.STATUS_REPRESENTATION[self.status]
        else:
            return format_html(
                self.STATUS_CASES[self.status], self.STATUS_REPRESENTATION[self.status]
            )
    colored_status.short_description = "Статус"

    def __str__(self):
        return '{}.{} - {} ({}-{})'.format(
            self.pk,
            self.date,
            self.group.name,
            self.starttime,
            self.endtime
        )


class Payment(models.Model):

    class Meta:
        verbose_name_plural = 'Платежи'
        unique_together = (('timestamp', 'child', 'pack'), )

    timestamp = models.DateTimeField()
    child = models.ForeignKey(
        Child, verbose_name='Ребенок', on_delete=models.CASCADE
    )
    pack = models.ForeignKey(
        Pack, verbose_name='Пакет', on_delete=models.CASCADE
    )

    def __str__(self):
        return '{}. Платёж: {} {} (Цена {} руб. | Тренировок {} | Заморозок {})'.format(
            self.pk,
            self.timestamp,
            self.child,
            self.pack.price,
            self.pack.trainings_count,
            self.pack.trainings_freeze_count,
        )
