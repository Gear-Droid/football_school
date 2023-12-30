from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import *


class GaleryMixin(View):

    def dispatch(self, request, *args, **kwargs):
        self.galery = Galery.objects.all()
        return super().dispatch(request, *args, **kwargs)


class PersonMixin(View):

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        person = Person.objects.filter(user=user).first()
        self.person = person
        return super().dispatch(request, *args, **kwargs)


class TrainingMixin(View):

    def dispatch(self, request, *args, **kwargs):
        self.training_pk = kwargs.get('training_pk')
        self.training = Training.objects.filter(pk=self.training_pk).first()
        self.group_children = self.training.group.children.all()
        self.training_status = self.TRAINING_STATUS[self.training.status]
        self.reserve_trainers = self.training.reserve_trainers.all()
        return super().dispatch(request, *args, **kwargs)


class TrainerMixin(View):

    def dispatch(self, request, *args, **kwargs):
        person = self.person
        self.trainer = Trainer.objects.filter(person=person).first()
        return super().dispatch(request, *args, **kwargs)


class ChildExistsMixin(View):

    def dispatch(self, request, *args, **kwargs):
        child_exists = Child.objects.filter(person=self.person).exists()
        if not child_exists:
            messages.add_message(
                request, messages.INFO,
                "Вас нет в списке детей, пожалуйста обратитесь к менеджеру!"
            )
            return HttpResponseRedirect(reverse('private_cabinet'))
        return super().dispatch(request, *args, **kwargs)
