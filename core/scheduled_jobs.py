import os
import psutil

from colorama import Fore, Style

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from samaneh.settings import (
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_SERVICE_NAME,
)

from core.configs import TEHRAN_TZ, MGT_FOR_DAILY_TASKS

from account.tasks import disable_expired_subscription

from dashboard.tasks import (
    dashboard_last_close_price,
    dashboard_buy_sell_orders_value,
    dashboard_total_index,
    dashboard_unweighted_index,
    dashboard_option_value_analysis,
)

from domestic_market.tasks import (
    populate_domestic_market_db,
    calculate_commodity_mean_domestic,
    calculate_production_sell_domestic,
    calculate_producers_yearly_value,
    calculate_monthly_sell_domestic,
    get_dollar_daily_price,
)

from fund.tasks import update_fund_info, get_all_fund_detail

from future_market.tasks import (
    update_derivative_info,
    update_future_base_equity,
    update_option_base_equity,
    update_future,
    update_option_result,
    check_future_active_contracts,
    check_option_active_contracts,
)

from option_market.tasks import update_option_data_from_tse, get_option_history

from stock_market.tasks import (
    update_market_watch,
    update_market_watch_indices,
    update_instrument_info,
    update_instrument_roi,
    stock_value_history,
    stock_value_change,
    stock_option_value_history,
    stock_option_value_change,
    stock_option_price_spread,
    get_monthly_activity_report_letter,
    update_stock_daily_history,
)

from global_market.tasks import calculate_commodity_means_global


def get_scheduler():
    total_cores = os.cpu_count()
    used_cores = total_cores // 2
    print(Fore.BLUE + f"Cores: {total_cores}, Used: {used_cores}" + Style.RESET_ALL)

    total_threads = psutil.Process().num_threads()
    print(
        Fore.BLUE + f"Threads: {total_threads}, Used: {total_threads}" + Style.RESET_ALL
    )

    jobstores = {
        "default": SQLAlchemyJobStore(
            url=f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVICE_NAME}:5432/{POSTGRES_DB}"
        )
    }

    executors = {
        "default": ThreadPoolExecutor(total_threads),
        "processpool": ProcessPoolExecutor(used_cores),
    }
    job_defaults = {
        "coalesce": True,
    }

    scheduler = BlockingScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=TEHRAN_TZ,
    )

    return scheduler


def add_account_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=disable_expired_subscription,
        id="disable_expired_subscription_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="1",
        minute="5",
    )

    return scheduler


def add_dashboard_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=dashboard_buy_sell_orders_value,
        id="dashboard_buy_sell_orders_value_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    scheduler.add_job(
        func=dashboard_last_close_price,
        id="dashboard_last_close_price_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    scheduler.add_job(
        func=dashboard_total_index,
        id="dashboard_total_index_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/6",
    )

    scheduler.add_job(
        func=dashboard_unweighted_index,
        id="dashboard_unweighted_index_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/6",
    )

    scheduler.add_job(
        func=dashboard_option_value_analysis,
        id="dashboard_option_value_analysis_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    return scheduler


def add_domestic_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=populate_domestic_market_db,
        id="populate_domestic_market_db_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="19",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_commodity_mean_domestic,
        id="calculate_commodity_mean_domestic_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="20",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_monthly_sell_domestic,
        id="calculate_monthly_sell_domestic_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="20",
        minute="30",
    )

    scheduler.add_job(
        func=calculate_production_sell_domestic,
        id="calculate_production_sell_domestic_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="21",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_producers_yearly_value,
        id="calculate_producers_yearly_value_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="21",
        minute="45",
    )

    scheduler.add_job(
        func=get_dollar_daily_price,
        id="get_dollar_daily_price_task",
        replace_existing=True,
        trigger="cron",
        minute="*/30",
    )

    return scheduler


def add_fund_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_fund_info,
        id="get_fund_detail_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="20",
        minute="10",
    )

    scheduler.add_job(
        func=get_all_fund_detail,
        id="get_all_fund_detail_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="9-17",
        minute="*/15",
    )

    return scheduler


def add_future_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_derivative_info,
        id="update_derivative_info_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="11-17",
        minute="*/2",
    )

    scheduler.add_job(
        func=update_future_base_equity,
        id="update_future_base_equity_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="22",
        minute="10",
    )

    scheduler.add_job(
        func=update_option_base_equity,
        id="update_option_base_equity_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="22",
        minute="11",
    )

    scheduler.add_job(
        func=update_future,
        id="update_future_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="11-17",
        second="*/55",
    )

    scheduler.add_job(
        func=update_option_result,
        id="update_option_result_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed, thu",
        hour="11-17",
        second="*/55",
    )

    scheduler.add_job(
        func=check_future_active_contracts,
        id="check_future_active_contracts_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="22",
        minute="12",
    )

    scheduler.add_job(
        func=check_option_active_contracts,
        id="check_option_active_contracts_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="22",
        minute="13",
    )

    return scheduler


def add_global_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=calculate_commodity_means_global,
        id="calculate_commodity_means_global_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="7",
        minute="10",
    )

    return scheduler


def add_option_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_option_data_from_tse,
        id="update_option_data_from_tse_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        second="*/40",
    )

    scheduler.add_job(
        func=get_option_history,
        id="get_option_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="1",
        minute="10",
    )

    return scheduler


def add_stock_market_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=update_market_watch,
        id="update_market_watch_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        second="*/45",
    )

    scheduler.add_job(
        func=update_market_watch_indices,
        id="update_market_watch_indices_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    scheduler.add_job(
        func=update_stock_daily_history,
        id="update_stock_daily_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="14",
        minute="35",
    )

    scheduler.add_job(
        func=update_instrument_info,
        id="update_instrument_info_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="17",
        minute="30",
    )

    scheduler.add_job(
        func=update_instrument_roi,
        id="update_instrument_roi_task",
        replace_existing=True,
        trigger="cron",
        hour="9-13",
        minute="*/45",
    )

    scheduler.add_job(
        func=stock_value_history,
        id="stock_value_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="5",
        minute="10",
    )

    scheduler.add_job(
        func=stock_value_change,
        id="stock_value_change_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    scheduler.add_job(
        func=stock_option_value_history,
        id="stock_option_value_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="7",
        minute="30",
    )

    scheduler.add_job(
        func=stock_option_value_change,
        id="stock_option_value_change_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    scheduler.add_job(
        func=stock_option_price_spread,
        id="stock_option_price_spread_task",
        replace_existing=True,
        trigger="cron",
        day_of_week="sat, sun, mon, tue, wed",
        hour="9-13",
        minute="*/5",
    )

    scheduler.add_job(
        func=get_monthly_activity_report_letter,
        id="get_monthly_activity_report_letter_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        trigger="cron",
        hour="6",
        minute="10",
    )

    return scheduler


def blocking_scheduler():

    scheduler = get_scheduler()

    scheduler = add_account_app_jobs(scheduler)
    scheduler = add_dashboard_app_jobs(scheduler)
    scheduler = add_domestic_market_app_jobs(scheduler)
    scheduler = add_fund_app_jobs(scheduler)
    scheduler = add_future_market_app_jobs(scheduler)
    scheduler = add_global_market_app_jobs(scheduler)
    scheduler = add_option_market_app_jobs(scheduler)
    scheduler = add_stock_market_app_jobs(scheduler)

    print(f"RUN_MAIN is >>>>>>>>>>>>>>>>>> {os.environ.get("RUN_MAIN", None)}")
    if os.environ.get("RUN_MAIN", None) != "true":
        print(Fore.GREEN + "APScheduler started successfully" + Style.RESET_ALL)
        scheduler.start()
    print(Fore.RED + "Another instance of APScheduler running" + Style.RESET_ALL)
