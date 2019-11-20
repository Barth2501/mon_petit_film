from celery import Celery
from app.views import app
from celery import shared_task


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    
    celery.conf.update(app.config)
    print(celery.conf['CELERY_BEAT_SCHEDULE'])
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery_app = make_celery(app)

@shared_task
def test():
    logger = test.get_logger()
    logger.info("Hello")
