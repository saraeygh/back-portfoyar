from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from core.configs import (
    THREAD_POOL_EXECUTER_WORKERS,
    PROCESS_POOL_EXECUTER_WORKERS,
)

from core.tasks import collect_user_stats

from domestic_market.tasks import (
    populate_domestic_market_db,
    calculate_commodity_mean_domestic,
    calculate_monthly_sell_domestic,
    calculate_production_sell_domestic,
    calculate_producers_yearly_value,
    get_dollar_daily_price,
)


from future_market.tasks import (
    update_derivative_info,
    update_base_equity,
    update_future,
    update_option_result,
)

from global_market.tasks import calculate_commodity_means_global


def add_core_app_jobs(scheduler):
    scheduler.add_job(func=collect_user_stats, trigger="cron", hour="23", minute="58")


def add_domestic_market_app_jobs(scheduler):
    scheduler.add_job(
        func=populate_domestic_market_db,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="8-19",
        minute="*/120",
    )

    scheduler.add_job(
        func=calculate_commodity_mean_domestic,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="8-19",
        minute="*/130",
    )

    scheduler.add_job(
        func=calculate_monthly_sell_domestic,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="8-19",
        minute="*/140",
    )

    scheduler.add_job(
        func=calculate_production_sell_domestic,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="8-19",
        minute="*/150",
    )

    scheduler.add_job(
        func=calculate_producers_yearly_value,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu, fri",
        hour="22",
        minute="10",
    )

    scheduler.add_job(
        func=get_dollar_daily_price,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu, fri",
        minute="*/30",
    )


def add_future_market_app_jobs(scheduler):
    scheduler.add_job(
        func=update_derivative_info,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="10-17",
        minute="*/1",
    )

    scheduler.add_job(
        func=update_base_equity,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="23",
    )

    scheduler.add_job(
        func=update_future,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="10-17",
        second="*/15",
    )

    scheduler.add_job(
        func=update_option_result,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="10-17",
        second="*/15",
    )


def add_global_market_app_jobs(scheduler):
    scheduler.add_job(
        func=calculate_commodity_means_global, trigger="cron", hour="7", minute="10"
    )


tehran_tz = timezone("Asia/Tehran")
executors = {
    "default": ThreadPoolExecutor(THREAD_POOL_EXECUTER_WORKERS),
    "processpool": ProcessPoolExecutor(PROCESS_POOL_EXECUTER_WORKERS),
}


def portfoyar_scheduler():
    scheduler = BackgroundScheduler(executors=executors, timezone=tehran_tz)

    add_core_app_jobs(scheduler)

    add_domestic_market_app_jobs(scheduler)

    add_future_market_app_jobs(scheduler)

    add_global_market_app_jobs(scheduler)

    scheduler.start()


# import logging
# from samaneh.settings.common import DEBUG
# logging.basicConfig()
# logging.getLogger("apscheduler").setLevel(logging.DEBUG)
