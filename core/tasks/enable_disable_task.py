import jdatetime as jdt

from celery import shared_task
from django_celery_beat.models import PeriodicTask

from core.configs import TEHRAN_TZ


def enable_task(task_name: str):
    try:
        task = PeriodicTask.objects.filter(name=task_name)
        task.update(enabled=True)
    except Exception:
        pass


def disable_task(task_name: str):
    try:
        task = PeriodicTask.objects.filter(name=task_name)
        task.update(enabled=False)
    except Exception:
        pass


@shared_task(name="enable_tasks_for_specific_time_task")
def enable_tasks_for_specific_time():
    now = jdt.datetime.now(tz=TEHRAN_TZ)
    hour = now.hour
    minute = now.minute

    enable_task(task_name="update_option_data_from_tse_task")

    if hour == 8 and minute == 30:
        print(f"Enabling tasks at {hour}:{minute} AM")
        enable_task(task_name="update_market_watch_task")

    if hour == 9 and minute == 0:
        print(f"Enabling tasks at {hour}:{minute} AM")
        enable_task(task_name="update_option_data_from_tse_task")

    if hour == 11 and minute == 0:
        print(f"Enabling tasks at {hour}:{minute} AM")
        enable_task(task_name="update_future_task")


@shared_task(name="disable_tasks_for_specific_time_task")
def disable_tasks_for_specific_time():
    now = jdt.datetime.now(tz=TEHRAN_TZ)
    hour = now.hour
    minute = now.minute

    if hour == 12 and minute == 30:
        print(f"Disabling tasks at {hour}:{minute} PM")
        disable_task(task_name="update_option_data_from_tse_task")

    if hour == 18 and minute == 0:
        print(f"Disabling tasks at {hour}:{minute} PM")
        disable_task(task_name="update_future_task")
        disable_task(task_name="update_market_watch_task")
