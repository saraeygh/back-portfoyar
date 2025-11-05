#!/bin/sh

celery -A samaneh beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
