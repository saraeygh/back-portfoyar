from celery_singleton import Singleton
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from samaneh.celery import app

# ENABLE & DISABLE TIMES
AT_0830_AM = "AT08:30AM"
AT_0900_AM = "AT09:00AM"
AT_1100_AM = "AT11:00AM"
AT_1230_PM = "AT12:30PM"
AT_1800_PM = "AT18:00PM"


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


@app.task(base=Singleton, name="enable_tasks_for_specific_time_task")
def enable_tasks_for_specific_time(time: str):
    if time == AT_0830_AM:
        print(f"Enabling tasks at {AT_0830_AM}")
        enable_task(frequency=45, task_name="update_market_watch_task")

    if time == AT_0900_AM:
        print(f"Enabling tasks at {AT_0900_AM}")
        enable_task(frequency=40, task_name="update_option_data_from_tse_task")

    if time == AT_1100_AM:
        print(f"Enabling tasks at {AT_1100_AM}")
        enable_task(frequency=55, task_name="update_future_task")


@app.task(base=Singleton, name="disable_tasks_for_specific_time_task")
def disable_tasks_for_specific_time(time: str):
    if time == AT_1230_PM:
        print(f"Disabling tasks at {AT_1230_PM}")
        disable_task(task_name="update_option_data_from_tse_task")

    if time == AT_1800_PM:
        print(f"Disabling tasks at {AT_1800_PM}")
        disable_task(task_name="update_future_task")
        disable_task(task_name="update_market_watch_task")
