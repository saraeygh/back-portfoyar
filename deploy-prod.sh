#!/bin/bash

set -e

if [ -f ".env.prod" ]; then
    echo "Found .env.prod file, continuing build process ..."
else
    echo "Error! .env.prod file not found, exiting ..."
    exit
fi

mkdir -p ./logs

sudo docker compose -f compose.prod.yml up --build -d \
    postgres_test \
    redis_test \
    mongodb_test \
    api_test \
    worker_test \
    beat_test \
    flower_test

sudo docker container restart nginx_test

sudo docker logs -f api_test