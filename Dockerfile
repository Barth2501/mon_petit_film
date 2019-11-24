# FROM python:3.7.2-alpine3.9
# RUN apk update
# RUN apk add --no-cache python3-dev libstdc++ && \
#     apk add --no-cache g++ && \
#     ln -s /usr/include/locale.h /usr/include/xlocale.h && \
#     pip3 install numpy && \
#     pip3 install pandas

# RUN apk add make automake gcc g++ subversion python3-dev
# RUN apk --update add bash nano
# RUN pip install numpy scipy pandas
# ENV STATIC_URL app/static
# ENV STATIC_PATH /home/lancelot/mon_petit_film/app/static
# COPY ./requirements.txt /home/lancelot/mon_petit_film/app/requirements.txt
# RUN pip install -r /home/lancelot/mon_petit_film/app/requirements.txt
# CMD ["echo", "coucou"]

FROM python:3.6
RUN pip install numpy pandas scipy
ENV PYTHONUNBUFFERED=1
ENV STATIC_URL app/static
ENV STATIC_PATH /home/lancelot/mon_petit_film/app/static
# ADD . /app
WORKDIR /app
COPY ./requirements.txt /home/lancelot/mon_petit_film/app/requirements.txt
RUN pip install -r /home/lancelot/mon_petit_film/app/requirements.txt
EXPOSE 8000
CMD ['python','manage.py','runserver']