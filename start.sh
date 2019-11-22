#!/bin/bash

app="mon_petit_film"
docker container kill mon_petit_film
docker rm mon_petit_film
docker build -t ${app} -f Dockerfile .
docker run -p 8000:80 \
  --name=${app} \
  -v $PWD:/app ${app}

# docker build -t pricing-model:latest -f Dockerfile --no-cache app