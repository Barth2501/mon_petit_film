#Create the docker image

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
