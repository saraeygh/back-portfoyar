#!/bin/sh

python manage.py collectstatic --no-input

python manage.py makemigrations
python manage.py migrate

python manage.py pre_start_functions

daphne -b 0.0.0.0 -p 9000 samaneh.asgi:application