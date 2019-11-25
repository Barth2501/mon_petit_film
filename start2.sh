#!/bin/bash


python3 manage.py runserver ; celery -A app.celery.celery_app worker -B --loglevel=info --detach
