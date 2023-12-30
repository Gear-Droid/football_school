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

    def get_form(self, request, obj=None, **kwargs):
        form = super(ScheduleAdmin, self).get_form(request, obj, **kwargs)
        print(form.base_fields['starttime'].__dict__)
        # form.base_fields['person'].label = 'Личность'
        return form


class GroupFilter(SimpleListFilter):
    title = 'Группа'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        groups = set([g for g in Group.objects.all()])
        return [(g.id, g.name) for g in groups]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.all()
        group_pk = self.value()
        group = Group.objects.filter(pk=group_pk).first()
        children_pk = [child.pk for child in group.children.all()]
        return queryset.filter(pk__in=children_pk)


class ChildAdmin(admin.ModelAdmin):
    list_display = (
        'person', 'groups', 'trainings_count', 'trainings_freeze_count', 'phone', 'email'
    )
    search_fields = [
        'person__phone',
        'person__user__email',
        'person__user__first_name',
        'person__user__last_name',
    ]
    list_filter = (GroupFilter,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'person':
            trainers_pk = list([x.person.pk for x in Trainer.objects.all()])
            managers_pk = list([x.person.pk for x in Manager.objects.all()])
            return ModelChoiceField(
                Person.objects.exclude(pk__in=trainers_pk+managers_pk)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ChildAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['person'].label = 'Личность'
        return form


class TrainerAdmin(admin.ModelAdmin):
    list_display = ('person', )
    search_fields = [
        'person__phone',
        'person__user__email',
        'person__user__first_name',
        'person__user__last_name',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'person':
            children_pk = list([x.person.pk for x in Child.objects.all()])
            managers_pk = list([x.person.pk for x in Manager.objects.all()])
            return ModelChoiceField(
                Person.objects.exclude(pk__in=children_pk+managers_pk)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(TrainerAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['person'].label = 'Личность'
        return form


class ManagerAdmin(admin.ModelAdmin):
    list_display = ('person', )
    search_fields = [
        'person__phone',
        'person__user__email',
        'person__user__first_name',
        'person__user__last_name',
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'person':
            trainers_pk = list([x.person.pk for x in Trainer.objects.all()])
            children_pk = list([x.person.pk for x in Child.objects.all()])
            return ModelChoiceField(
                Person.objects.exclude(pk__in=trainers_pk+children_pk)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ManagerAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['person'].label = 'Личность'
        return form


class AgeCategoryFilter(SimpleListFilter):
    title = 'Возрастная категория'
    parameter_name = 'age_category'

    def lookups(self, request, model_admin):
        age_categories = list([ac for ac in AgeCategory.objects.all().order_by('min_age', 'max_age')])
        return [(ac.id, "{} - {}".format(ac.min_age, ac.max_age)) for ac in age_categories]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.all()
        age_category_pk = self.value()
        age_category = AgeCategory.objects.filter(pk=age_category_pk).first()
        return queryset.filter(age_category=age_category)


class DepartmentFilter(SimpleListFilter):
    title = 'Отделение'
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        departments = list([dep for dep in Department.objects.all().order_by('-pk')])
        return [(dep.id, dep.name) for dep in departments]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.all()
        department_pk = self.value()
        department = Department.objects.filter(pk=department_pk).first()
        schedules_with_department = Schedule.objects.filter(department=department)
        unique_pks = set()
        for schedule in schedules_with_department:
            for sc in schedule.groups.all():
                unique_pks.add(sc.pk)
        return queryset.filter(pk__in=unique_pks)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'age_category', 'departments')
    search_fields = ['name', ]
    ordering = ['-name', ]
    list_filter = (AgeCategoryFilter, DepartmentFilter, )


class TrainingAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'starttime', 'endtime', 'group', 'department', 'colored_status'
    )
    search_fields = [
        'date', 'starttime', 'endtime', 'department__name'
    ]
    ordering = ['-date', '-starttime', '-endtime']
    list_filter = ('department', 'status', 'group')


# Register your models here.
admin.site.register(PreRegisterUserEmail)
admin.site.register(Galery, GaleryAdmin)
admin.site.register(PhotoInGalery)
admin.site.register(News)
admin.site.register(Person)
admin.site.register(Child, ChildAdmin)
admin.site.register(Trainer, TrainerAdmin)
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Pack)
admin.site.register(AgeCategory)
admin.site.register(Group, GroupAdmin)
admin.site.register(Department)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(Payment)
