from django import forms
from django.forms import ModelForm
from django.core.validators import EmailValidator, ValidationError, RegexValidator

from .models import PreRegisterUserEmail, User


class RegisterUserForm(forms.ModelForm):

    email = forms.EmailField(
        max_length=254,
        required=True, disabled=True)
    username = forms.CharField(
        min_length=8, max_length=32,
        help_text='8-32 символа. Буквы, цифры и ./+/-/_ только.'
    )
    first_name = forms.CharField(min_length=1, max_length=128, required=True)
    last_name = forms.CharField(min_length=1, max_length=128, required=True)
    phone = forms.CharField(
        min_length=18, max_length=18,
        widget=forms.TextInput(attrs={'data-mask': "+7 (000) 000-00-00"}),
        required=True,
        initial='+7 ('
    )
    password = forms.CharField(
        min_length=8, max_length=32, widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        min_length=8, max_length=32, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'phone',
            'password',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Электронная почта'
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Данный почтовый адрес уже зарегистрирован в системе.')
        return email

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        if '@' in username:
            raise forms.ValidationError(f'Знак @ не должен содержаться в логине.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Имя {username} занято.')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают.')
        return self.cleaned_data


class LoginForm(forms.ModelForm):

    login = forms.CharField(max_length=254)
    password = forms.CharField(
        min_length=8, max_length=32,
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = (
            'login',
            'password',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = 'Логин или email'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        login = self.cleaned_data['login'].lower()
        password = self.cleaned_data.get('password')
        username_exists = User.objects.filter(username=login).exists()
        email_exists = User.objects.filter(email=login).exists()
        if not (username_exists or email_exists):
            raise forms.ValidationError(f'Пользователь {login} не найден.')
        if '@' in login:
            user = User.objects.filter(email=login).first()
        else:
            user = User.objects.filter(username=login).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль.')
        return self.cleaned_data
