#!/bin/sh

celery -A samaneh beat & \ 
celery -A samaneh flower --basic-auth=arman:Por@1403 --url-prefix=flower & \
celery -A samaneh worker
