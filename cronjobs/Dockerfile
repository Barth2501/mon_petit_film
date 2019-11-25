FROM python:3.6
RUN pip install numpy pandas scipy

RUN mkdir -p /app
WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . /app/

ENV PYTHONUNBUFFERED=1
ENV STATIC_URL app/static
ENV STATIC_PATH /home/lancelot/mon_petit_film/app/static

# COPY ./requirements.txt /home/lancelot/mon_petit_film/app/requirements.txt
# RUN pip install -r /home/lancelot/mon_petit_film/app/requirements.txt
# EXPOSE 8000
# CMD ["celery","-A","celery.celery_app","worker","-B","--loglevel=info"]