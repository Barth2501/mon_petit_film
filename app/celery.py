from celery import Celery
from app.views import app
from celery import shared_task
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(app.import_name, result_backend=app.config['result_backend'],
                    broker=app.config['CELERY_BROKER_URL'],timezone = 'Europe/London')

    celery.conf.update(app.config)
    celery.conf.beat_schedule = {
        'send-mail-on-monday': {
            'task': 'app.tasks.send_mail.send_mail_flask',
            'schedule': crontab(minute="*"),
        },
    }
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery_app = make_celery(app)


# @celery_app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(30.0, test.s('world'), expires=10)

#     # Executes every Monday morning at 7:30 a.m.
#     sender.add_periodic_task(
#         crontab(hour=7, minute=30, day_of_week=1),
#         test.s('Happy Mondays!'),
#     )


@shared_task
def test():
    print('oui')
