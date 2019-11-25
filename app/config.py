from celery.schedules import crontab

CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_IMPORTS = ('cronjobs.tasks.test', 'cronjobs.tasks.send_mail')
CELERYBEAT_SCHEDULE = {
    'send-mail-on-monday': {
        'task': 'cronjobs.tasks.send_mail.send_mail_flask',
        'schedule': crontab(day_of_week='sunday',minute=0, hour=8),
    }
}
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "barthelemy.lancelot@zenrooms.com"
MAIL_PASSWORD = "lancelot2501"
MAIL_DEFAULT_SENDER = "barthelemy.lancelot@zenrooms.com"
MONGO_DBNAME = "restdb"
MONGO_URI = "mongodb://heroku_1hj3v1h2:hiiq0l9nuj1fdffsqffr6spc1p@ds113799.mlab.com:13799/heroku_1hj3v1h2?retryWrites=false"
