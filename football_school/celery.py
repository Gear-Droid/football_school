import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_school.settings')
app = Celery('football_school')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.worker_concurrency = 2
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


"""@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(3.0, app.task(test).s('IDIOT hello 3'), name='add every 3')

def test(arg):
    print(arg)
    return arg
"""


app.conf.beat_schedule = {
    'trainings_scheduler': {
        'task': 'mainapp.tasks.schedule_maker',
        'schedule': 4.0,
        'args': ()
    },
}
app.conf.timezone = 'UTC'


# Run CELERY
# celery -A football_school worker -B -l info
