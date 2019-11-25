from celery import Celery
from app.views import app
from app.svd import recommend_movies
from flask_mail import Message
from app.views import mail
from app.classes.user import User
from flask import render_template


def make_celery(app):
    celery = Celery(
        app.import_name,
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        broker=app.config["CELERY_BROKER_URL"],
        timezone="Europe/London",
    )

    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery_app = make_celery(app)


@celery_app.task
def send_mail_user(username, id):
    user = User.get(username=username)
    reco_movies = recommend_movies(id, 5)[1]
    dict_reco_movies = reco_movies.to_dict("records")
    msg = Message(
        subject="Recommended movies", recipients=[user.json["emailAddress"]]
    )
    # msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(
        "mail.html", dict_reco_movies=dict_reco_movies, user=user.json
    )
    mail.send(msg)
