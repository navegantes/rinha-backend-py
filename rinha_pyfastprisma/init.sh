#!/bin/bash

docker compose rm -f
docker compose down --remove-orphans --rmi all

if [ $# -lt 1 ];
  then
    docker compose -f docker-compose.yml up --build
  else
    docker compose -f $1 up --build
fi