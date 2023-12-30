"""football_school URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path, reverse
from .views import (
    HomePageView,
    AboutUsView,
    GaleryView,
    GaleryDetailView,
    ContactsView,
    SendApplication,
    PrivateCabinetView,
    LoginView,
    RegisterFormView,
    PreRegisterView,
    TrainingDetailView,
    TrainingScheduleView,
    PaymentView,
    DepartmentPacksView,
    DepartmentPacksPaymentView,
)


urlpatterns = [
    path('', HomePageView.as_view(), name='base'),
    path('about/', AboutUsView.as_view(), name='about_us'),
    path('galery/', GaleryView.as_view(), name='galery'),
    path('galery/<str:slug>/', GaleryDetailView.as_view(), name='galery_detail'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('send_application', SendApplication.as_view(), name='send_application'),
    path('lc/', PrivateCabinetView.as_view(), name='private_cabinet'),
    path('lc/login/', LoginView.as_view(), name='login_to_private_cabinet'),
    path('lc/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('lc/register/',
        PreRegisterView.as_view(), name='preregister_to_private_cabinet'
    ),
    re_path(r'^lc/register_form/(?P<wherefrom>[^/]+)/$', 
        RegisterFormView.as_view(), name='register_to_private_cabinet'
    ),
    path('lc/trainings_schedule/', TrainingScheduleView.as_view(), name='trainings_schedule'),
    path('lc/trainings_schedule/training/<int:training_pk>', TrainingDetailView.as_view(), name='training_detail'),
    path('lc/payment/', PaymentView.as_view(), name='payment'),
    path('lc/payment/<int:department_id>/', DepartmentPacksView.as_view(), name='department_packs'),
    path('lc/payment/<int:department_id>/<int:pack_id>', DepartmentPacksPaymentView.as_view(), name='department_packs_payment'),
]
