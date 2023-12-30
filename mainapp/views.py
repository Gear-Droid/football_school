import telebot

from smtplib import SMTPException
from unicodedata import name
from cryptography import fernet

from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.utils import IntegrityError
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from .utils import (
    validate_email,
    is_registered,
    send_invitation_to_register,
    decrypt_it,
    make_registration_link,
    get_trainings_schedule_for_child,
    get_trainings_schedule_for_trainer,
    mark_children,
    get_training_children_pks,
    get_not_editable,
)
from .forms import RegisterUserForm, LoginForm
from .mixins import (
    GaleryMixin,
    PersonMixin,
    TrainingMixin,
    TrainerMixin,
    ChildExistsMixin,
)


class HomePageView(View):

    def get(self, request, *args, **kwargs):
        context = {
            'Title': 'Главная страница',
        }
        return render(request, 'base.html', context=context)


class AboutUsView(View):

    def get(self, request, *args, **kwargs):
        context = {
            'Title': 'О нас',
        }
        return render(request, 'mainapp/about_us.html', context=context)


class GaleryView(GaleryMixin, View):

    def get(self, request, *args, **kwargs):
        galery_catalog = self.galery.order_by('-pk')
        context = {
            'Title': 'Галерея',
            'galery_catalog': galery_catalog,
        }
        return render(request, 'mainapp/galery/galery.html', context=context)


class GaleryDetailView(GaleryMixin, View):

    def get(self, request, *args, **kwargs):
        galery_slug = kwargs.get('slug')
        galery = self.galery.get(slug=galery_slug)
        photo_in_galery = PhotoInGalery.objects.filter(galery=galery).order_by('-pk')
        context = {
            'Title': galery.header,
            'galery': galery,
            'photo': photo_in_galery,
        }
        return render(request, 'mainapp/galery/galery_detail.html', context=context)


class SendApplication(View):

    def get(self, request, *args, **kwargs):
        name, phone, age = request.GET.get('name'), request.GET.get('phone'), request.GET.get('age')
        # Токен, который выдает @botfather
        bot = telebot.TeleBot('5284601816:AAG1HmY4cDf2e5LQQuBHzvcpaQdlJyje4T0')
        # Адрес телеграм-канала, начинается с @
        CHAT_ID = '-1001751034019'
        try:
            bot.send_message(CHAT_ID, f'❗️❗️❗️ НОВАЯ ЗАЯВКА ❗️❗️❗️\n\n⚽️ имя: {name}\n📞 тел.: {phone}\n👦🏻 возраст ребенка: {age}')
        except telebot.apihelper.ApiTelegramException:
            messages.add_message(
                request, messages.ERROR,
                "Не удалось отправить Вашу заявку менеджеру, свяжитесь, пожалуйста, с нами по одному из контактов на сайте!"
            )
        else:
            messages.add_message(
                request, messages.INFO,
                "Наш менеджер свяжется с Вами в ближайшее время!"
            )
        return HttpResponseRedirect(reverse('base'))


class ContactsView(View):

    def get(self, request, *args, **kwargs):
        context = {
            'Title': 'Контакты',
        }
        return render(request, 'mainapp/contacts.html', context=context)


class LoginView(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('private_cabinet'))
        form = LoginForm(request.POST or None)
        context = {
            'Title': 'Вход в личный кабинет',
            'form': form,
        }
        return render(request, 'mainapp/lc/login.html', context=context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            clean_login = form.cleaned_data['login'].lower()
            password = form.cleaned_data['password']
            if '@' in clean_login:
                user = User.objects.filter(email=clean_login).first()
                username = user.username
            else:
                username = clean_login
            user = authenticate(
                username=username,
                password=password
            )
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('private_cabinet'))
        context = {
            'Title': 'Вход в личный кабинет',
            'form': form,
        }
        return render(request, 'mainapp/lc/login.html', context=context)


class PreRegisterView(View):

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        context = {
            'Title': 'Регистрация',
        }
        if email is not None:
            email = email.lower()
            validated = validate_email(email)
            if not validated:
                messages.add_message(
                    request, messages.INFO,
                    "Вы ввели некорректный email!"
                )
            else:
                if is_registered(email=email):
                    messages.add_message(
                        request, messages.INFO,
                        "Email уже зарегистрирован!"
                    )
                else:
                    PreRegisterUserEmail.objects.get_or_create(email=email)
                    try:
                        send_invitation_to_register(email)
                    except SMTPException as err:
                        print(err)
                        messages.add_message(
                            request, messages.INFO,
                            "Не удалось отправить письмо на почту {}".format(email)
                        )
                        return render(request, 'mainapp/lc/preregister.html', context=context)
                    else:
                        messages.add_message(
                            request, messages.INFO,
                            "Письмо отправлено на почту {}".format(email)
                        )
                        return HttpResponseRedirect(reverse('base'))
        return render(request, 'mainapp/lc/preregister.html', context=context)


class RegisterFormView(View):

    def get(self, request, *args, **kwargs):
        key = settings.CRYPTOGRAPHY_KEY
        wherefrom_bytes_message = bytes(kwargs.get('wherefrom'), "utf-8")
        try:
            email_id, email = self.get_lower_email(wherefrom_bytes_message)
        except (ValueError, fernet.InvalidToken):
            return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))
        form = RegisterUserForm(request.POST or None, initial={'email': email})
        if PreRegisterUserEmail.objects.filter(email=email).exists():
            if not email_id == PreRegisterUserEmail.objects.get(email=email).pk:
                return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))
            context = {
                'Title': 'Создание нового пользователя',
                'form': form,
            }
            return render(request, 'mainapp/lc/register.html', context=context)
        return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        key = settings.CRYPTOGRAPHY_KEY
        wherefrom_bytes_message = bytes(kwargs.get('wherefrom'), "utf-8")
        try:
            email_id, email = self.get_lower_email(wherefrom_bytes_message)
        except (ValueError, fernet.InvalidToken):
            return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))
        form = RegisterUserForm(request.POST or None, initial={'email': email})
        if form.is_valid():
            try:
                pre_reg_email = PreRegisterUserEmail.objects.filter(email=email).first()
                if not pre_reg_email:
                    return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))
                address = make_registration_link(email, key)
                new_user = form.save(commit=False)
                new_user.email = form.cleaned_data['email'].lower()
                new_user.username = form.cleaned_data['username'].lower()
                new_user.first_name = form.cleaned_data['first_name']
                new_user.last_name = form.cleaned_data['last_name']
                new_user.save()
                new_user.set_password(form.cleaned_data['password'])
                new_user.save()
                person = Person.objects.create(user=new_user)
                person.phone = form.cleaned_data['phone']
                person.save()
                user = authenticate(
                    username=new_user.username,
                    password=new_user.password
                )
                pre_reg_email.delete()
            except IntegrityError:
                messages.add_message(
                    request, messages.INFO,
                    "Не удалось зарегистрироваться! Попробуйте снова."
                )
                return HttpResponseRedirect(address)
            if user:
                return HttpResponseRedirect(reverse('private_cabinet'))
            else:
                return HttpResponseRedirect(reverse('base'))
        context = {
            'Title': 'Создание нового пользователя',
            'form': form,
        }
        return render(request, 'mainapp/lc/register.html', context=context)

    def get_lower_email(self, bytes_message):
        # try:
        #     message = decrypt_it(wherefrom_bytes_message, key)
        # except fernet.InvalidToken:
        #     return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))
        key = settings.CRYPTOGRAPHY_KEY
        message = decrypt_it(bytes_message, key)
        email, email_id = message.split('-&id&-')
        email = email.lower()
        email_id = int(email_id)
        # try:
        #     email_id = int(email_id)
        # except ValueError:
        #     return HttpResponseRedirect(reverse('preregister_to_private_cabinet'))
        return email_id, email


class PrivateCabinetView(LoginRequiredMixin, PersonMixin, View):

    login_url = '/lc/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        child_exists = Child.objects.filter(person=self.person).exists()
        context = {
            'Title': 'Личный кабинет',
            'child_exists': child_exists,
        }
        return render(request, 'mainapp/lc/lc.html', context=context)


class TrainingScheduleView(LoginRequiredMixin, PersonMixin, View):

    login_url = '/lc/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        person = self.person
        child_exists = Child.objects.filter(person=person).exists()
        trainer_exists = Trainer.objects.filter(person=person).exists()
        if not child_exists and not trainer_exists:
            messages.add_message(
                request, messages.INFO,
                "Вас нет в списке тренеров и детей. Пожалуйста, обратитесь к менеджеру!"
            )
            return HttpResponseRedirect(reverse('private_cabinet'))
        child = Child.objects.filter(person=person).first()
        trainer = Trainer.objects.filter(person=person).first()
        schedule_header, schedule_list, statuses, training_pks = [], [], [], []
        if trainer:
            schedule_header, schedule_list, statuses, training_pks = get_trainings_schedule_for_trainer(
                trainer=trainer
            )
        elif child:
            schedule_header, schedule_list, statuses, training_pks = get_trainings_schedule_for_child(
                child=child
            )
        is_empty = True
        if len(schedule_list) > 0:
            is_empty = False
        context = {
            'Title': 'Расписание',
            'schedule_header': schedule_header,
            'schedule_list': schedule_list,
            'statuses': statuses,
            'training_pks': training_pks,
            'is_trainer': trainer,
            'is_empty': is_empty,
        }
        return render(request, 'mainapp/lc/schedule/trainings_schedule.html', context=context)


class TrainingDetailView(LoginRequiredMixin, PersonMixin, TrainingMixin, TrainerMixin, View):

    login_url = '/lc/login/'
    redirect_field_name = 'redirect_to'

    TRAINING_STATUS = {
        'not_stated': 'Неопределенное',
        'done': 'Выполнена',
        'not_took_place': 'Не состоялась',
    }

    def get(self, request, *args, **kwargs):
        trainer_in_group, trainer_in_reserve, trainer_exists = False, False, False
        if self.trainer:
            trainer_exists = True
        if self.training.group.trainers.filter(pk=self.trainer.pk).exists():
            trainer_in_group = True
        if self.training.reserve_trainers.filter(pk=self.trainer.pk).exists():
            trainer_in_reserve = True
        if trainer_exists and (trainer_in_group or trainer_in_reserve):
            not_editable = get_not_editable(self.training)
            training_children_pks = get_training_children_pks(self.training.pk)
            context = {
                'Title': 'Детали тренировки',
                'training': self.training,
                'training_status': self.training_status,
                'reserve_trainers': self.reserve_trainers,
                'children': self.group_children,
                'training_children_pks': training_children_pks,
                'not_editable': not_editable,
            }
            return render(request, 'mainapp/lc/schedule/training/training_detail.html', context=context)
        return HttpResponseRedirect(reverse('private_cabinet'))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        children_pk_to_mark = set(request.POST.getlist('child'))
        try:
            trainer_in_group, trainer_in_reserve, trainer_exists = False, False, False
            if self.trainer:
                trainer_exists = True
            if self.training.group.trainers.filter(pk=self.trainer.pk).exists():
                trainer_in_group = True
            if self.training.reserve_trainers.filter(pk=self.trainer.pk).exists():
                trainer_in_reserve = True
            if trainer_exists and (trainer_in_group or trainer_in_reserve):
                not_editable = get_not_editable(self.training)
                if not_editable:
                    messages.add_message(
                        request, messages.INFO,
                        "Не удалось отметить детей! Состояние тренировки неизменяемое."
                    )
                    return HttpResponseRedirect(reverse(
                        'training_detail',
                        kwargs={'training_pk': self.training.pk},
                    ))
                success = mark_children(
                    children_pk_to_mark, self.group_children, self.training
                )
                training_children_pks = get_training_children_pks(self.training.pk)
                context = {
                    'Title': 'Детали тренировки',
                    'training': self.training,
                    'training_status': self.training_status,
                    'reserve_trainers': self.reserve_trainers,
                    'children': self.group_children,
                    'training_children_pks': training_children_pks,
                    'not_editable': not_editable,
                }
                messages.add_message(
                    request, messages.INFO,
                    "Дети успешно отмечены."
                )
                return render(request, 'mainapp/lc/schedule/training/training_detail.html', context=context)
            return HttpResponseRedirect(reverse('private_cabinet'))
        except IntegrityError:
            messages.add_message(
                request, messages.INFO,
                "Не удалось отметить игроков в базе данных! Попробуйте снова."
            )
            return HttpResponseRedirect(reverse(
                    'training_detail',
                    kwargs={'training_pk': self.training.pk},
                ))


class PaymentView(LoginRequiredMixin, PersonMixin, ChildExistsMixin, View):

    login_url = '/lc/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        departments = Department.objects.all()
        context = {
            'Title': 'Выбор отделения для оплаты',
            'departments': departments,
        }
        return render(request, 'mainapp/lc/payment/payment.html', context=context)


class DepartmentPacksView(LoginRequiredMixin, PersonMixin, ChildExistsMixin, View):

    login_url = '/lc/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        department_id = kwargs.get('department_id')
        dep_model = Department.objects.filter(pk=department_id).first()
        if dep_model is None:
            return HttpResponseRedirect(reverse('payment'))
        available_packs = dep_model.packs.all()
        context = {
            'Title': 'Выбор пакета тренировок',
            'available_packs': available_packs,
        }
        return render(request, 'mainapp/lc/payment/department_packs.html', context=context)


class DepartmentPacksPaymentView(LoginRequiredMixin, PersonMixin, ChildExistsMixin, View):

    login_url = '/lc/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        department_id = kwargs.get('department_id')
        pack_id = kwargs.get('pack_id')
        dep_model = Department.objects.filter(pk=department_id).first()
        pack_model = dep_model.packs.filter(pk=pack_id).first()
        if dep_model is None:
            return HttpResponseRedirect(reverse('payment'))
        if pack_model is None:
            return HttpResponseRedirect(reverse('payment'))
        context = {
            'Title': 'Оплата выбранного пакета тренировок',
            'dep_model': dep_model,
            'pack_model': pack_model,
        }
        return render(request, 'mainapp/lc/payment/department_packs_payment.html', context=context)
