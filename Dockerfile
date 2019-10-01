FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7
RUN apk --update add bash nano
ENV STATIC_URL app/static
ENV STATIC_PATH /home/lancelot/mon_petit_film/app/static
COPY ./requirements.txt /home/lancelot/mon_petit_film/app/requirements.txt
RUN pip install -r /home/lancelot/mon_petit_film/app/requirements.txt