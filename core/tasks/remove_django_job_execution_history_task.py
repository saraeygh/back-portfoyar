from datetime import datetime as dt, timedelta as td

from django_apscheduler.models import DjangoJobExecution

from core.configs import TEHRAN_TZ
from core.utils import run_main_task


def remove_django_job_execution_history_main():
    one_week_ago = dt.now(tz=TEHRAN_TZ) - td(days=7)
    DjangoJobExecution.objects.filter(run_time__lt=one_week_ago).delete()


def remove_django_job_execution_history():
    run_main_task(
        main_task=remove_django_job_execution_history_main,
        daily=True,
    )
