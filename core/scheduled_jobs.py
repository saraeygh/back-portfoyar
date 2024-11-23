import os
import psutil

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from core.configs import TEHRAN_TZ

from core.tasks import collect_user_stats

from dashboard.tasks import dashboard

from domestic_market.tasks import (
    populate_domestic_market_db,
    calculate_commodity_mean_domestic,
    calculate_production_sell_domestic,
    calculate_producers_yearly_value,
    calculate_monthly_sell_domestic,
    get_dollar_daily_price,
)

from future_market.tasks import (
    update_derivative_info,
    update_base_equity,
    update_future,
    update_option_result,
)

from option_market.tasks import update_option_data_from_tse, get_option_history

from stock_market.tasks import (
    update_market_watch,
    update_market_watch_indices,
    update_stock_raw_adjusted_history,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_value_change,
    stock_option_value_change,
    stock_option_price_spread,
    get_monthly_activity_report_letter,
)

from global_market.tasks import calculate_commodity_means_global

from colorama import Fore, Style


def get_scheduler():
    total_cores = os.cpu_count()
    used_cores = total_cores // 2
    print(Fore.BLUE + f"Cores: {total_cores}, Used: {used_cores}" + Style.RESET_ALL)

    total_threads = psutil.Process().num_threads()
    print(
        Fore.BLUE + f"Threads: {total_threads}, Used: {total_threads}" + Style.RESET_ALL
    )

    executors = {
        "default": ThreadPoolExecutor(total_threads),
        "processpool": ProcessPoolExecutor(used_cores),
    }
    job_defaults = {
        "coalesce": True,
    }

    scheduler = BlockingScheduler(
        executors=executors, job_defaults=job_defaults, timezone=TEHRAN_TZ
    )

    return scheduler


def add_core_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=collect_user_stats,
        id="collect_user_stats_task",
        trigger="cron",
        day_of_week="*",
        hour="23",
        minute="58",
    )

    scheduler.add_job(
        func=dashboard,
        id="dashboard_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-17",
        minute="*/5",
    )

    return scheduler


def add_domestic_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=populate_domestic_market_db,
        id="populate_domestic_market_db_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="19",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_commodity_mean_domestic,
        id="calculate_commodity_mean_domestic_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="20",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_monthly_sell_domestic,
        id="calculate_monthly_sell_domestic_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="20",
        minute="30",
    )

    scheduler.add_job(
        func=calculate_production_sell_domestic,
        id="calculate_production_sell_domestic_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="21",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_producers_yearly_value,
        id="calculate_producers_yearly_value_task",
        trigger="cron",
        day_of_week="*",
        hour="21",
        minute="45",
    )

    scheduler.add_job(
        func=get_dollar_daily_price,
        id="get_dollar_daily_price_task",
        trigger="cron",
        day_of_week="*",
        minute="*/30",
    )

    return scheduler


def add_future_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_derivative_info,
        id="update_derivative_info_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2, 3",
        hour="10-17",
        minute="*/1",
    )

    scheduler.add_job(
        func=update_base_equity,
        id="update_base_equity_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2, 3",
        hour="22",
        minute="10",
    )

    scheduler.add_job(
        func=update_future,
        id="update_future_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2, 3",
        hour="10-17",
        second="*/30",
    )

    scheduler.add_job(
        func=update_option_result,
        id="update_option_result_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2, 3",
        hour="10-17",
        second="*/45",
    )

    return scheduler


def add_option_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_option_data_from_tse,
        id="update_option_data_from_tse_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        second="*/40",
    )

    scheduler.add_job(
        func=get_option_history,
        id="get_option_history_task",
        trigger="cron",
        day_of_week="*",
        hour="1",
        minute="10",
    )

    return scheduler


def add_stock_market_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=update_market_watch,
        id="update_market_watch_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        second="*/20",
    )

    scheduler.add_job(
        func=update_market_watch_indices,
        id="stock_market_watch_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        second="*/55",
    )

    scheduler.add_job(
        func=update_stock_raw_adjusted_history,
        id="update_stock_raw_adjusted_history_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="2",
        minute="10",
    )

    scheduler.add_job(
        func=update_instrument_info,
        id="update_instrument_info_task",
        trigger="cron",
        day_of_week="*",
        hour="4",
        minute="10",
    )

    scheduler.add_job(
        func=update_instrument_roi,
        id="update_instrument_roi_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        minute="*/5",
    )

    scheduler.add_job(
        func=stock_value_history,
        id="stock_value_history_task",
        trigger="cron",
        day_of_week="*",
        hour="5",
        minute="10",
    )

    scheduler.add_job(
        func=stock_value_change,
        id="stock_value_change_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        minute="*/1",
    )

    scheduler.add_job(
        func=stock_option_value_change,
        id="stock_option_value_change_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        minute="*/5",
    )

    scheduler.add_job(
        func=stock_option_price_spread,
        id="stock_option_price_spread_task",
        trigger="cron",
        day_of_week="5, 6, 0, 1, 2",
        hour="8-15",
        minute="*/1",
    )

    scheduler.add_job(
        func=get_monthly_activity_report_letter,
        id="get_monthly_activity_report_letter_task",
        trigger="cron",
        day_of_week="*",
        hour="6",
        minute="10",
    )

    return scheduler


def add_global_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=calculate_commodity_means_global,
        id="calculate_commodity_means_global_task",
        trigger="cron",
        day_of_week="*",
        hour="7",
        minute="10",
    )

    return scheduler


def blocking_scheduler():

    scheduler = get_scheduler()

    scheduler = add_core_app_jobs(scheduler)
    scheduler = add_domestic_market_app_jobs(scheduler)
    scheduler = add_future_market_app_jobs(scheduler)
    scheduler = add_option_market_app_jobs(scheduler)
    scheduler = add_stock_market_app_jobs(scheduler)
    scheduler = add_global_market_app_jobs(scheduler)

    print(Fore.GREEN + "APScheduler started successfully" + Style.RESET_ALL)
    scheduler.start()
