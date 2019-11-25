from celery import shared_task
from flask_mail import Message
from app.views import mail
from flask import render_template
from app.classes.user import User
from app.svd import recommend_movies


@shared_task
def send_mail_flask():
    for user in User.all():
        try:
            reco_movies = recommend_movies(user.mongo_id, 5)[1]
        except ValueError:
            continue
        dict_reco_movies = reco_movies.to_dict('records')
        msg = Message(subject='Recommended movies',
                      recipients=[user.json['emailAddress']])
        # msg.body = render_template(template+'.txt', **kwargs)
        msg.html = render_template(
            'mail.html', dict_reco_movies=dict_reco_movies, user=user.json)
        mail.send(msg)

