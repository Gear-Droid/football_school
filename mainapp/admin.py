from django.contrib import admin
from django.forms import ModelForm
from .models import (
    PreRegisterUserEmail,
    Galery,
    PhotoInGalery,
    News,
    Person,
    Child,
    Trainer,
    Manager,
    Pack,
    AgeCategory,
    Group,
    Department,
    Schedule,
    Training,
    Payment
)


class GaleryAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class GaleryAdmin(admin.ModelAdmin):
    # Поле slug будет заполнено на основе поля header
    prepopulated_fields = {"slug": ("header", )}


# Register your models here.
admin.site.register(PreRegisterUserEmail)
admin.site.register(Galery, GaleryAdmin)
admin.site.register(PhotoInGalery)
admin.site.register(News)
admin.site.register(Person)
admin.site.register(Child)
admin.site.register(Trainer)
admin.site.register(Manager)
admin.site.register(Pack)
admin.site.register(AgeCategory)
admin.site.register(Group)
admin.site.register(Department)
admin.site.register(Schedule)
admin.site.register(Training)
admin.site.register(Payment)
