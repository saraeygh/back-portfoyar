import os
from celery import Celery
from celery.schedules import crontab

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


# ENABLE & DISABLE TIMES
AT_0830_AM = "08:30 AM"
AT_0900_AM = "09:00 AM"
AT_1100_AM = "11:00 AM"
AT_1230_PM = "12:30 PM"
AT_1800_PM = "18:00 PM"

app.conf.beat_schedule = {
    #
    # ENABLING TASKS
    "enable_tasks_at_0830_am": {
        "task": "enable_tasks_for_specific_time_task",
        "schedule": crontab(hour=8, minute=30, day_of_week="6,0,1,2,3"),
        "args": (AT_0830_AM,),
    },
    "enable_tasks_at_0900_am": {
        "task": "enable_tasks_for_specific_time_task",
        "schedule": crontab(hour=9, minute=0, day_of_week="6,0,1,2,3"),
        "args": (AT_0900_AM,),
    },
    "enable_tasks_at_1100_am": {
        "task": "enable_tasks_for_specific_time_task",
        "schedule": crontab(hour=11, minute=0, day_of_week="6,0,1,2,3,4"),
        "args": (AT_1100_AM,),
    },
    #
    # DISABLING TASKS
    "disable_tasks_at_1230_pm": {
        "task": "disable_tasks_for_specific_time_task",
        "schedule": crontab(hour=12, minute=30, day_of_week="6,0,1,2,3"),
        "args": (AT_1230_PM,),
    },
    "disable_tasks_at_1800_pm": {
        "task": "disable_tasks_for_specific_time_task",
        "schedule": crontab(hour=18, minute=0, day_of_week="6,0,1,2,3,4"),
        "args": (AT_1800_PM,),
    },
}
