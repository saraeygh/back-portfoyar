#!/bin/bash

set -e

if [ -f ".env.test" ]; then
    echo "Found .env.test file, continuing build process ..."
else
    echo "Error! .env.test file not found, exiting ..."
    exit
fi

mkdir -p ./logs

sudo docker compose -f compose.test.yml up --build -d \
    postgres_test \
    redis_test \
    mongodb_test \
    api_test \
    apscheduler_test

sudo docker container restart nginx_test

sudo docker logs -f api_test