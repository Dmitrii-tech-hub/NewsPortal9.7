from celery import Celery
from celery.schedules import crontab

app = Celery('simpleapp')

app.conf.beat_schedule = {
    'send-weekly-posts': {
        'task': 'simpleapp.tasks.send_new_post_email',
        'schedule': crontab(day_of_week=0, hour=0, minute=0),
    },
}
