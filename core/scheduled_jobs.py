import os
import psutil

from colorama import Fore, Style

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from django_apscheduler.jobstores import DjangoJobStore

from core.configs import (
    TEHRAN_TZ,
    MGT_FOR_DAILY_TASKS,
    MGT_FOR_PREIODIC_TASKS,
    FIVE_DAYS_WEEK,
    SIX_DAYS_WEEK,
    TSETMC_MARKET_HOURS,
    DERIVATIVE_MARKET_HOURS,
    TSE_PLUS_DERIVATIVE_MARKET_HOURS,
)

from core.tasks import remove_django_job_execution_history, is_market_open_today
from account.tasks import disable_expired_subscription

from dashboard.tasks import (
    dashboard_last_close_price,
    dashboard_buy_sell_orders_value,
    dashboard_total_index,
    dashboard_unweighted_index,
    dashboard_option_value_analysis,
    dashboard_change_percent_ranges_count,
    dashboard_market_money_flow,
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

from option_market.tasks import (
    update_option_data_from_tse,
    get_option_history,
    calculate_daily_option_value,
)

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


def get_cores_threads():
    total_cores = os.cpu_count()
    used_cores = total_cores // 2
    print(Fore.BLUE + f"Cores: {total_cores}, Used: {used_cores}" + Style.RESET_ALL)

    total_threads = psutil.Process().num_threads()
    print(
        Fore.BLUE + f"Threads: {total_threads}, Used: {total_threads}" + Style.RESET_ALL
    )

    return used_cores, total_threads


def get_executors(used_cores, total_threads):
    executors = {
        "default": ThreadPoolExecutor(total_threads),
        "processpool": ProcessPoolExecutor(used_cores),
    }

    return executors


def get_scheduler():
    used_cores, total_threads = get_cores_threads()
    executors = get_executors(used_cores, total_threads)

    scheduler = BlockingScheduler(executors=executors, timezone=TEHRAN_TZ)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    return scheduler


def add_core_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=remove_django_job_execution_history,
        id="remove_django_job_execution_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="1",
        minute="20",
    )

    scheduler.add_job(
        func=is_market_open_today,
        id="is_market_open_today_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="9",
        minute="1",
    )

    return scheduler


def add_account_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=disable_expired_subscription,
        id="disable_expired_subscription_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="1",
        minute="5",
    )

    return scheduler


def add_dashboard_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=dashboard_buy_sell_orders_value,
        id="dashboard_buy_sell_orders_value_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=dashboard_last_close_price,
        id="dashboard_last_close_price_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=dashboard_total_index,
        id="dashboard_total_index_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=dashboard_unweighted_index,
        id="dashboard_unweighted_index_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=calculate_daily_option_value,
        id="calculate_daily_option_value_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour="23",
        minute="5",
    )

    scheduler.add_job(
        func=dashboard_option_value_analysis,
        id="dashboard_option_value_analysis_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=dashboard_change_percent_ranges_count,
        id="dashboard_change_percent_ranges_count_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=dashboard_market_money_flow,
        id="dashboard_market_money_flow_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSE_PLUS_DERIVATIVE_MARKET_HOURS,
        minute="*/2",
    )

    return scheduler


def add_domestic_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=populate_domestic_market_db,
        id="populate_domestic_market_db_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour="19",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_commodity_mean_domestic,
        id="calculate_commodity_mean_domestic_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour="20",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_monthly_sell_domestic,
        id="calculate_monthly_sell_domestic_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour="20",
        minute="30",
    )

    scheduler.add_job(
        func=calculate_production_sell_domestic,
        id="calculate_production_sell_domestic_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour="21",
        minute="10",
    )

    scheduler.add_job(
        func=calculate_producers_yearly_value,
        id="calculate_producers_yearly_value_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="21",
        minute="45",
    )

    scheduler.add_job(
        func=get_dollar_daily_price,
        id="get_dollar_daily_price_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        minute="*/5",
    )

    return scheduler


def add_fund_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_fund_info,
        id="get_fund_detail_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="23",
        minute="30",
    )

    scheduler.add_job(
        func=get_all_fund_detail,
        id="get_all_fund_detail_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour=TSE_PLUS_DERIVATIVE_MARKET_HOURS,
        minute="*/15",
    )

    return scheduler


def add_future_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_derivative_info,
        id="update_derivative_info_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour=DERIVATIVE_MARKET_HOURS,
        minute="*/2",
    )

    scheduler.add_job(
        func=update_future_base_equity,
        id="update_future_base_equity_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour="22",
        minute="10",
    )

    scheduler.add_job(
        func=update_option_base_equity,
        id="update_option_base_equity_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour="22",
        minute="11",
    )

    scheduler.add_job(
        func=update_future,
        id="update_future_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour=DERIVATIVE_MARKET_HOURS,
        second="*/55",
    )

    scheduler.add_job(
        func=update_option_result,
        id="update_option_result_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=SIX_DAYS_WEEK,
        hour=DERIVATIVE_MARKET_HOURS,
        minute="*/1",
    )

    scheduler.add_job(
        func=check_future_active_contracts,
        id="check_future_active_contracts_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="22",
        minute="12",
    )

    scheduler.add_job(
        func=check_option_active_contracts,
        id="check_option_active_contracts_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
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
        coalesce=True,
        trigger="cron",
        hour="7",
        minute="10",
    )

    return scheduler


def add_option_market_app_jobs(scheduler: BlockingScheduler):
    scheduler.add_job(
        func=update_option_data_from_tse,
        id="update_option_data_from_tse_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        second="*/40",
    )

    scheduler.add_job(
        func=get_option_history,
        id="get_option_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="1",
        minute="10",
    )

    return scheduler


def add_stock_market_app_jobs(scheduler: BlockingScheduler):

    scheduler.add_job(
        func=update_market_watch,
        id="update_market_watch_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSE_PLUS_DERIVATIVE_MARKET_HOURS,
        second="*/45",
    )

    scheduler.add_job(
        func=update_market_watch_indices,
        id="update_market_watch_indices_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSE_PLUS_DERIVATIVE_MARKET_HOURS,
        minute="*/3",
    )

    scheduler.add_job(
        func=update_stock_daily_history,
        id="update_stock_daily_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="18",
        minute="35",
    )

    scheduler.add_job(
        func=update_instrument_info,
        id="update_instrument_info_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="17",
        minute="30",
    )

    scheduler.add_job(
        func=update_instrument_roi,
        id="update_instrument_roi_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour=TSE_PLUS_DERIVATIVE_MARKET_HOURS,
        minute="*/30",
    )

    scheduler.add_job(
        func=stock_value_history,
        id="stock_value_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="5",
        minute="10",
    )

    scheduler.add_job(
        func=stock_value_change,
        id="stock_value_change_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSE_PLUS_DERIVATIVE_MARKET_HOURS,
        minute="*/3",
    )

    scheduler.add_job(
        func=stock_option_value_history,
        id="stock_option_value_history_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="7",
        minute="30",
    )

    scheduler.add_job(
        func=stock_option_value_change,
        id="stock_option_value_change_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/3",
    )

    scheduler.add_job(
        func=stock_option_price_spread,
        id="stock_option_price_spread_task",
        misfire_grace_time=MGT_FOR_PREIODIC_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        day_of_week=FIVE_DAYS_WEEK,
        hour=TSETMC_MARKET_HOURS,
        minute="*/3",
    )

    scheduler.add_job(
        func=get_monthly_activity_report_letter,
        id="get_monthly_activity_report_letter_task",
        misfire_grace_time=MGT_FOR_DAILY_TASKS,
        replace_existing=True,
        coalesce=True,
        trigger="cron",
        hour="6",
        minute="10",
    )

    return scheduler


def blocking_scheduler():

    scheduler = get_scheduler()

    scheduler = add_core_app_jobs(scheduler)
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
