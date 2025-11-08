import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samaneh.settings")

app = Celery("samaneh")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task
def delete_old_task_results(days_to_keep=1):
    from django_celery_results.models import TaskResult
    from datetime import datetime, timedelta

    threshold_date = datetime.now() - timedelta(days=days_to_keep)
    TaskResult.objects.filter(date_done__lt=threshold_date).delete()
