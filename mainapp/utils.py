import os
import datetime

from smtplib import SMTPException
from cryptography.fernet import Fernet

from django.conf import settings
from django.core.validators import EmailValidator, ValidationError
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse
from .models import *


def validate_email(value):
    validator = EmailValidator()
    try:
        validator(value)
    except ValidationError:
        return False
    else:
        return True


def is_registered(email):
    if User.objects.filter(email=email).exists():
        return True
    return False


def encrypt_it(message, key):
    """
        Зашифровывает сообщение
    """
    f = Fernet(key)
    encrypted = f.encrypt(message)
    # Encrypt the bytes. The returning object is of type bytes
    return encrypted


def decrypt_it(encrypted, key):
    """
        Расшифровывает сообщение
    """
    f = Fernet(key)
    message = f.decrypt(encrypted)
    # Decrypt the bytes. The returning object is of type bytes
    message = message.decode()
    return message


def make_registration_link(email, key):
    email = email.lower()
    pre_reg_email, _ = PreRegisterUserEmail.objects.get_or_create(email=email)
    email_id = pre_reg_email.pk
    message = bytes(email + '-&id&-' + str(email_id), encoding='utf8')
    encrypted = encrypt_it(message, key).decode()
    # address = 'http://localhost:8000' + os.path.join(
    address = 'http://' + settings.BASE_URL + os.path.join(
        settings.BASE_DIR, reverse(
            'register_to_private_cabinet',
            kwargs={'wherefrom': encrypted}
        )
    )
    return address


def send_invitation_to_register(email):
    key = settings.CRYPTOGRAPHY_KEY
    address = make_registration_link(email, key)
    print(address)
    message = address
    send_mail(
        'Регистрация в личном кабинете',  # Тема письма
        message,  # Текст письма
        settings.EMAIL_HOST_USER,  # От кого
        [email],  # Кому
        fail_silently=False,
    )
    return address


def get_trainings_schedule_for_trainer(trainer):
    groups = Group.objects.filter(trainers=trainer).all()
    schedule_header = ('Дата', 'Время', 'Отделение')
    schedule_list = []
    if groups.first() is not None:
        result_Q = Q()
        for group in groups:
            result_Q = result_Q | (Q(group=group))
        if Training.objects.filter(reserve_trainers=trainer).first() is not None:
            result_Q = result_Q | Q(reserve_trainers=trainer)
        trainings = Training.objects.filter(result_Q).order_by('-date', '-starttime')
    else:
        trainings = []
    training_pks = []
    statuses = []
    for t in trainings:
        if t.status == Training.STATUS_DONE:
            mark = 'GREEN_mark'
        if t.status == Training.STATUS_NOT_STATED:
            mark = 'WHITE_mark'
        if t.status == Training.STATUS_NOT_TOOK_PLACE:
            mark = 'YELLOW_mark'
        statuses.append(mark)
        training_pks.append(t.pk)
        date = t.date
        time = "{} - {}".format(
            t.starttime.strftime("%H:%M"), t.endtime.strftime("%H:%M")
        )
        schedule_list.append((date, time, t.department))
    return schedule_header, schedule_list, statuses, training_pks


def get_trainings_schedule_for_child(child):
    groups = Group.objects.filter(children=child).all()
    schedule_header = ('Дата', 'Время', 'Отделение')
    schedule_list = []
    if groups.first() is not None:
        result_Q = Q()
        for group in groups:
            result_Q = result_Q | (Q(group=group))
        today = datetime.date.today()
        trainings = Training.objects.filter(result_Q).filter(
            date__range=[today-datetime.timedelta(days=40), today+datetime.timedelta(days=40)]
        ).order_by('-date', '-starttime')
    else:
        trainings = []
    statuses = []
    trainings_with_child = Training.objects.filter(children=child).all()
    trainings_with_child_pks = set()
    for t_with_c in trainings_with_child:
        trainings_with_child_pks.add(t_with_c.pk)
    training_pks = []
    for t in trainings:
        if t.status == Training.STATUS_DONE:
            if t.pk in trainings_with_child_pks:
                mark = 'GREEN_mark'
            else:
                mark = 'RED_mark'
        if t.status == Training.STATUS_NOT_STATED:
            mark = 'WHITE_mark'
        if t.status == Training.STATUS_NOT_TOOK_PLACE:
            mark = 'YELLOW_mark'
        statuses.append(mark)
        training_pks.append(t.pk)
        date = t.date
        time = "{} - {}".format(
            t.starttime.strftime("%H:%M"), t.endtime.strftime("%H:%M")
        )
        schedule_list.append((date, time, t.department))
    return schedule_header, schedule_list, statuses, training_pks


def mark_children(children_pk_to_mark, group_children, training):
    for child in group_children:
        if str(child.pk) in children_pk_to_mark:
            if not child in Training.objects.filter(pk=training.pk).first().children.all():
                training_with_child = training.children.add(child)
        elif child in Training.objects.filter(pk=training.pk).first().children.all():
            training_with_child = training.children.remove(child)


def get_training_children_pks(training_pk):
    training_children_pks = []
    training_with_children = Training.objects.filter(pk=training_pk).first()
    training_children = training_with_children.children.all()
    for training_child in training_children:
        training_children_pks.append(training_child.pk)
    return training_children_pks


def get_not_editable(training):
    not_editable = False
    status_not_editable = False
    if training.status == Training.STATUS_NOT_TOOK_PLACE or  \
        training.status == Training.STATUS_DONE:
        status_not_editable = True
    now = datetime.datetime.now()
    then = datetime.datetime(
        training.date.year,
        training.date.month,
        training.date.day,
    )
    delta = now - then
    if delta.days > 0 or status_not_editable:
        not_editable = True
    return not_editable
