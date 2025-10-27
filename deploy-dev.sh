#!/bin/bash

set -e

if [ -f ".env.dev" ]; then
    echo "Found .env.dev file, continuing build process ..."
else
    echo "Error! .env.dev file not found, exiting ..."
    exit
fi

mkdir -p ./logs

sudo docker compose -f compose.dev.yml up --build -d \
    postgres_test \
    redis_test \
    mongodb_test \
    apscheduler_test

sudo docker container restart nginx_test

sudo docker logs -f apscheduler_test