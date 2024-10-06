import os

from celery import Celery
from celery.schedules import crontab

REDIS_SERVICE_NAME = os.environ.setdefault("REDIS_SERVICE_NAME", "localhost")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samaneh.settings.local")

app = Celery("samaneh", broker=f"redis://{REDIS_SERVICE_NAME}:6379/0")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

DOMESTIC_MARKET_SCHEDULE = {
    "populate_domestic_market_db_task": {
        "task": "populate_domestic_market_db_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/120",
        ),
    },
    "calculate_commodity_mean_task_domestic": {
        "task": "calculate_commodity_mean_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/130",
        ),
    },
    "calculate_monthly_sell_task_domestic": {
        "task": "calculate_monthly_sell_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/140",
        ),
    },
    "calculate_production_sell_task_domestic": {
        "task": "calculate_production_sell_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/150",
        ),
    },
    "get_dollar_daily_price_task_domestic": {
        "task": "get_dollar_daily_price_task_domestic",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4, 5",
            minute="*/30",
        ),
    },
    "calculate_producers_yearly_value": {
        "task": "calculate_producers_yearly_value",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="22",
            minute="10",
        ),
    },
}


FUTURE_MARKET_SCHEDULE = {
    "update_future_info_task": {
        "task": "update_future_info_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3, 4",
            hour="8-22",
            minute="*/1",
        ),
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
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/1",
        ),
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
    "stock_market_watch_task": {
        "task": "stock_market_watch_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/5",
        ),
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
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="9-19",
            minute="*/3",
        ),
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
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/5",
        ),
    },
    "stock_option_value_change_task": {
        "task": "stock_option_value_change_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/5",
        ),
    },
    "stock_option_price_spread_task": {
        "task": "stock_option_price_spread_task",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",
            hour="8-19",
            minute="*/6",
        ),
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


SAVE_OPTIONS_BASED_ON_DIFFERENT_VOLUME_COEFFICIENTS = {
    "save_options_based_on_volume_comparison_with_different_coefficienets": {
        "task": "save_options_based_on_volume_comparison_with_different_coefficienets",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",  # Monday to Friday (0=Sunday, 6=Saturday)
            hour=f"8-13",  # Specify the hour range (e.g., "8-17" for 8 AM to 5 PM)
            minute="*/5",  # Every minute within the specified hours
        ),
    }
}


PROCESS_TRANSACTIONS_BASED_ON_VOLUME_CHANGE_AND_COEFFICIENETS = {
    "process_transactions_based_on_coefficients_and_volume_change_with_respect_to_the_last_transaction": {
        "task": "process_transactions_based_on_coefficients_and_volume_change_with_respect_to_the_last_transaction",
        "schedule": crontab(
            day_of_week="6, 0, 1, 2, 3",  # Monday to Friday (0=Sunday, 6=Saturday)
            hour=f"8-13",  # Specify the hour range (e.g., "8-17" for 8 AM to 5 PM)
            minute="*/5",  # Every minute within the specified hours
        ),
    }
}

app.conf.beat_schedule = {
    **DOMESTIC_MARKET_SCHEDULE,
    **GLOBAL_MARKET_SCHEDULE,
    **OPTION_MARKET_SCHEDULE,
    **STOCK_MARKET_SCHEDULE,
    # **SAVE_OPTIONS_BASED_ON_DIFFERENT_VOLUME_COEFFICIENTS,
    # **PROCESS_TRANSACTIONS_BASED_ON_VOLUME_CHANGE_AND_COEFFICIENETS,
}
