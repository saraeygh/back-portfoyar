#!/bin/sh

celery -A samaneh flower --port=5555 --url_prefix=/flower
