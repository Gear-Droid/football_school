import datetime

from celery import shared_task
from mainapp.models import Schedule, Training


def recalculate_trainings():
    today = datetime.date.today()
    for train in Training.objects.filter(date__gte=today, status='not_stated').order_by('date'):
        train_weekday = train.date.weekday() + 1
        res = Schedule.objects.filter(
            train_day=train_weekday,
            groups=train.group,
            department=train.department,
            starttime=train.starttime,
            endtime=train.endtime,
        ).first()
        if res is None:
            train.delete()

    for i in range(30):
        training_date = datetime.date.today() + datetime.timedelta(days=i)
        weekday_number = training_date.weekday() + 1
        for schedule_training in Schedule.objects.filter(train_day=weekday_number):
            for group in schedule_training.groups.all():
                new_training, created = Training.objects.get_or_create(
                    date=training_date,
                    department=schedule_training.department,
                    group=group,
                    starttime=schedule_training.starttime,
                    endtime =schedule_training.endtime,
                )
                if created:
                    new_training.save()


@shared_task
def schedule_maker():
    recalculate_trainings()
