import jdatetime as jdt

from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from core.configs import TEHRAN_TZ


def enable_task(frequency: int, task_name: str):
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=frequency,
        period=IntervalSchedule.SECONDS,
    )

    task, _ = PeriodicTask.objects.get_or_create(
        name=task_name, defaults={"task": task_name, "interval": schedule}
    )
    task.enabled = True
    task.save()


def disable_task(task_name: str):
    try:
        task = PeriodicTask.objects.get(name=task_name)
        task.enabled = False
        task.save()
    except PeriodicTask.DoesNotExist:
        pass


@shared_task(name="enable_tasks_for_specific_time_task")
def enable_tasks_for_specific_time():
    now = jdt.datetime.now(tz=TEHRAN_TZ)
    hour = now.hour
    minute = now.minute

    if hour == 8 and minute == 30:
        print(f"Enabling tasks at {hour}:{minute} AM")
        enable_task(frequency=45, task_name="update_market_watch_task")

    if hour == 9 and minute == 0:
        print(f"Enabling tasks at {hour}:{minute} AM")
        enable_task(frequency=40, task_name="update_option_data_from_tse_task")

    if hour == 11 and minute == 0:
        print(f"Enabling tasks at {hour}:{minute} AM")
        enable_task(frequency=55, task_name="update_future_task")


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
