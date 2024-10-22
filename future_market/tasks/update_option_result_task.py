import json
import pandas as pd
import jdatetime
from celery import shared_task

from core.configs import FUTURE_REDIS_DB
from core.utils import RedisInterface, task_timing

from future_market.models import OPTION_INFO
from future_market.utils import (
    get_options_base_equity_info,
    OPTION_COLUMNS,
    populate_all_strategy,
)

redis_conn = RedisInterface(db=FUTURE_REDIS_DB)


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


@task_timing
@shared_task(name="update_option_result_task")
def update_option_result():
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

    populate_all_strategy(option_data)
