import json
import pandas as pd
import jdatetime
from celery import shared_task

from core.configs import FUTURE_REDIS_DB, AUTO_MODE, MANUAL_MODE
from core.utils import RedisInterface, task_timing, is_scheduled

from future_market.models import OPTION_INFO
from future_market.utils import (
    get_options_base_equity_info,
    OPTION_COLUMNS,
    populate_all_strategy,
)

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)

REPLACE_SYMBOL_DICT = {
    "قرارداد اختیار معامله فروش ": "ا.ف ",
    "قرارداد اختیار معامله خرید": "ا.خ ",
    "سررسید": "",
    "ریال": "",
    "با قیمت اعمال": "",
    "مبتنی بر قرارداد": "",
    "ماه": "",
    "واحدهای سرمایه گذاری صندوق طلای": "",
    "صندوق طلای": "",
    "  ": " ",
}


def add_symbol_to_option_data(row):
    contract_code = str(row.get("CallContractCode"))
    symbol = contract_code[0:2]
    return symbol


def add_remained_day(row):
    end_date = str(row.get("end_date"))
    year, month, day = end_date.split("/")
    year, month, day = int(year), int(month), int(day)
    end_date = jdatetime.date(year=year, month=month, day=day)
    today_date = jdatetime.date.today()
    remained_day = (end_date - today_date).days

    return remained_day


def change_str_last_update_to_int(row, col_name):
    try:
        last_update = str(row.get(col_name))
        last_update = int((last_update.split(" - ")[1]).replace(":", ""))
        return last_update
    except Exception:
        pass

    try:
        last_update = str(row.get(col_name))
        last_update = int(last_update.replace(":", ""))
    except Exception:
        last_update = 0

    return last_update


def shorten_option_symbol(row, col_name):
    try:
        shortened_option_symbol = str(row.get(col_name))
        for to_replace, replacement in REPLACE_SYMBOL_DICT.items():
            shortened_option_symbol = shortened_option_symbol.replace(
                to_replace, replacement
            )
        return shortened_option_symbol
    except Exception:
        return str(row.get(col_name))


def update_option_result_main():
    option_data = json.loads(redis_conn.client.get(name=OPTION_INFO))
    option_data = pd.DataFrame(option_data)

    option_data["symbol"] = option_data.apply(add_symbol_to_option_data, axis=1)
    base_equity_data = get_options_base_equity_info()
    option_data = pd.merge(
        left=option_data, right=base_equity_data, on="symbol", how="left"
    )

    option_data.rename(columns=OPTION_COLUMNS, inplace=True)
    option_data = option_data[list(OPTION_COLUMNS.values())]
    option_data["remained_day"] = option_data.apply(add_remained_day, axis=1)

    option_data["call_last_update"] = option_data.apply(
        change_str_last_update_to_int, axis=1, args=("call_last_update",)
    )

    option_data["put_last_update"] = option_data.apply(
        change_str_last_update_to_int, axis=1, args=("put_last_update",)
    )

    option_data["base_equity_last_update"] = option_data.apply(
        change_str_last_update_to_int, axis=1, args=("base_equity_last_update",)
    )

    option_data["call_symbol"] = option_data.apply(
        shorten_option_symbol, axis=1, args=("call_symbol",)
    )
    option_data["put_symbol"] = option_data.apply(
        shorten_option_symbol, axis=1, args=("put_symbol",)
    )
    populate_all_strategy(option_data)


@task_timing
@shared_task(name="update_option_result_task")
def update_option_result(run_mode: str = AUTO_MODE):
    # if run_mode == MANUAL_MODE or is_scheduled(
    #     weekdays=[0, 1, 2, 3, 4, 5], start_hour=10, end_hour=17
    # ):
    update_option_result_main()
