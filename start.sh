#!/bin/bash
app="mon_petit_film"
docker container kill mon_petit_film
docker rm mon_petit_film
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD:/app ${app}