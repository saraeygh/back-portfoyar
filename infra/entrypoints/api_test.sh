#!/bin/sh

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
python manage.py pre_start_functions
gunicorn samaneh.wsgi --bind=0.0.0.0:9000
