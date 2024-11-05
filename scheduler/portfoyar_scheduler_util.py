from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from core.configs import (
    THREAD_POOL_EXECUTER_WORKERS,
    PROCESS_POOL_EXECUTER_WORKERS,
)

from global_market.tasks import calculate_commodity_means_global

tehran_tz = timezone("Asia/Tehran")
executors = {
    "default": ThreadPoolExecutor(THREAD_POOL_EXECUTER_WORKERS),
    "processpool": ProcessPoolExecutor(PROCESS_POOL_EXECUTER_WORKERS),
}


def portfoyar_scheduler():
    scheduler = BackgroundScheduler(executors=executors, timezone=tehran_tz)

    scheduler.add_job(calculate_commodity_means_global, "cron", hour="7", minute="10")

    scheduler.start()


# import logging
# from samaneh.settings.common import DEBUG
# logging.basicConfig()
# logging.getLogger("apscheduler").setLevel(logging.DEBUG)
