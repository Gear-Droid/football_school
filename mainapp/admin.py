from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.forms import ModelForm, ModelChoiceField
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


class ScheduleAdmin(admin.ModelAdmin):
    DAY_CHOICES = (
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    )

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'train_day':
            kwargs['choices'] = self.DAY_CHOICES
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class StatusFilter(SimpleListFilter):
    title = ('Status')

    parameter_name = 'trainings_count'


class ChildAdmin(admin.ModelAdmin):
    list_display = ('person', 'trainings_count', 'trainings_freeze_count', 'phone', 'email')
    search_fields = [
        'person__phone',
        'person__user__email',
        'person__user__first_name',
        'person__user__last_name',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'person':
            childs_pk = list([x.person.pk for x in Child.objects.all()])
            return ModelChoiceField(
                Person.objects.filter(pk__in=childs_pk)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Register your models here.
admin.site.register(PreRegisterUserEmail)
admin.site.register(Galery, GaleryAdmin)
admin.site.register(PhotoInGalery)
admin.site.register(News)
admin.site.register(Person)
admin.site.register(Child, ChildAdmin)
admin.site.register(Trainer)
admin.site.register(Manager)
admin.site.register(Pack)
admin.site.register(AgeCategory)
admin.site.register(Group)
admin.site.register(Department)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Training)
admin.site.register(Payment)
