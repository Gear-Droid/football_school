import datetime

from celery import shared_task
from mainapp.models import Schedule, Training
from .utils import recalculate_trainings


@shared_task
def schedule_maker():
    recalculate_trainings()
