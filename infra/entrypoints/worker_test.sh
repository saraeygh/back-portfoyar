#!/bin/sh

celery -A samaneh worker -l info --concurrency=4
