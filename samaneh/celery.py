import os

from celery import Celery
from celery.schedules import crontab

from core.configs import CELERY_REDIS_DB

REDIS_SERVICE_NAME = os.environ.setdefault("REDIS_SERVICE_NAME", "localhost")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samaneh.settings.local")

app = Celery("samaneh", broker=f"redis://{REDIS_SERVICE_NAME}:6379/{CELERY_REDIS_DB}")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

CORE_SCHEDULE = {
    "collect_user_stats_task": {
        "task": "collect_user_stats_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="23",
            minute="58",
        ),
    },
    "dashboard_task": {
        "task": "dashboard_task",
        "schedule": 60 * 5,
    },
}

DOMESTIC_MARKET_SCHEDULE = {
    "populate_domestic_market_db_task": {
        "task": "populate_domestic_market_db_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="19",
            minute="20",
        ),
    },
    "calculate_commodity_mean_task_domestic": {
        "task": "calculate_commodity_mean_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="20",
            minute="10",
        ),
    },
    "calculate_monthly_sell_task_domestic": {
        "task": "calculate_monthly_sell_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="20",
            minute="30",
        ),
    },
    "calculate_production_sell_task_domestic": {
        "task": "calculate_production_sell_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="20",
            minute="55",
        ),
    },
    "calculate_producers_yearly_value_task": {
        "task": "calculate_producers_yearly_value_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="22",
            minute="10",
        ),
    },
    "get_dollar_daily_price_task_domestic": {
        "task": "get_dollar_daily_price_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            minute="*/30",
        ),
    },
}


FUTURE_MARKET_SCHEDULE = {
    "update_derivative_info_task": {
        "task": "update_derivative_info_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="10-17",
            minute="*/1",
        ),
    },
    "update_base_equity_task": {
        "task": "update_base_equity_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4",
            hour="23",
        ),
    },
    "update_future_task": {
        "task": "update_future_task",
        "schedule": 14,
    },
    "update_option_result_task": {
        "task": "update_option_result_task",
        "schedule": 15,
    },
}

GLOBAL_MARKET_SCHEDULE = {
    "calculate_commodity_means_task_global": {
        "task": "calculate_commodity_means_task_global",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="7",
            minute="10",
        ),
    },
}

OPTION_MARKET_SCHEDULE = {
    "update_option_data_from_tse_task": {
        "task": "update_option_data_from_tse_task",
        "schedule": 15,
    },
    "get_option_history_task": {
        "task": "get_option_history_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="3",
            minute="10",
        ),
    },
    "populate_option_total_volume_task": {
        "task": "populate_option_total_volume_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="4",
            minute="50",
        ),
    },
    "option_volume_strategy_result_task": {
        "task": "option_volume_strategy_result_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="5",
            minute="30",
        ),
    },
}


STOCK_MARKET_SCHEDULE = {
    "update_market_watch_task": {
        "task": "update_market_watch_task",
        "schedule": 12,
    },
    "stock_market_watch_task": {
        "task": "stock_market_watch_task",
        "schedule": 13,
    },
    "update_stock_raw_adjusted_history_task": {
        "task": "update_stock_raw_adjusted_history_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="5",
            minute="10",
        ),
    },
    "stock_market_update_instrument_info": {
        "task": "stock_market_update_instrument_info",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="6",
            minute="10",
        ),
    },
    "update_instrument_roi_task": {
        "task": "update_instrument_roi_task",
        "schedule": 45,
    },
    "stock_value_history_task": {
        "task": "stock_value_history_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="16",
            minute="10",
        ),
    },
    "stock_value_change_task": {
        "task": "stock_value_change_task",
        "schedule": 30,
    },
    "stock_option_value_change_task": {
        "task": "stock_option_value_change_task",
        "schedule": 30,
    },
    "stock_option_price_spread_task": {
        "task": "stock_option_price_spread_task",
        "schedule": 30,
    },
    "get_monthly_activity_report_letter_task": {
        "task": "get_monthly_activity_report_letter_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            hour="4",
            minute="10",
        ),
    },
}


app.conf.beat_schedule = {
    **CORE_SCHEDULE,
    **DOMESTIC_MARKET_SCHEDULE,
    **GLOBAL_MARKET_SCHEDULE,
    **OPTION_MARKET_SCHEDULE,
    **STOCK_MARKET_SCHEDULE,
    **FUTURE_MARKET_SCHEDULE,
}
