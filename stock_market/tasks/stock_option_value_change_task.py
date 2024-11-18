from celery import shared_task
import pandas as pd
from core.utils import MongodbInterface, RedisInterface, is_scheduled, task_timing

from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    RIAL_TO_MILLION_TOMAN,
    OPTION_REDIS_DB,
    AUTO_MODE,
    MANUAL_MODE,
)

from stock_market.utils import CALL_OPTION, PUT_OPTION, get_market_watch_data_from_redis

from colorama import Fore, Style


redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def get_instrument_info():
    mongo_client = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name="instrument_info"
    )
    instrument_info = list(mongo_client.collection.find({}, {"_id": 0}))
    instrument_info = pd.DataFrame(instrument_info)

    return instrument_info


def get_last_options(option_type):
    last_options = redis_conn.get_list_of_dicts(list_key="option_data")
    last_options = pd.DataFrame(last_options)
    if option_type == CALL_OPTION:
        last_options = last_options[
            ["call_ins_code", "base_equity_symbol", "call_value", "call_close_price"]
        ]
        return last_options

    elif option_type == PUT_OPTION:
        last_options = last_options[
            ["put_ins_code", "base_equity_symbol", "put_value", "put_close_price"]
        ]

    else:
        return last_options

    return last_options


def get_asset_options_value_change(options, option_type):
    close_price_col = "call_close_price"
    if option_type == PUT_OPTION:
        close_price_col = "put_close_price"

    value_col = "call_value"
    if option_type == PUT_OPTION:
        value_col = "put_value"

    base_equities = options["base_equity_symbol"].unique().tolist()
    options_list = list()
    for base_equity in base_equities:

        try:
            base_equity_options: pd.DataFrame = options[
                options["base_equity_symbol"] == base_equity
            ]
            base_equity_options["month_mean_value"] = (
                base_equity_options["month_mean_volume"]
                * 1000
                * base_equity_options[close_price_col]
            ) / RIAL_TO_MILLION_TOMAN
            base_equity_options = base_equity_options[
                base_equity_options["month_mean_value"] != 0
            ]

            last_mean = (
                float(base_equity_options[value_col].mean()) / RIAL_TO_MILLION_TOMAN
            )
            month_mean = float(base_equity_options["month_mean_value"].mean())
            value_change = last_mean / month_mean
        except Exception:
            last_mean = 0
            month_mean = 0
            value_change = 0

        new_value_change = {
            "symbol": base_equity,
            "last_mean": last_mean,
            "month_mean": month_mean,
            "value_change": value_change,
        }
        options_list.append(new_value_change)

    option_value_change = pd.DataFrame(options_list)
    option_value_change.dropna(inplace=True)

    return option_value_change


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def add_pe(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    eps = row.get("eps")
    try:
        pe = close_mean / eps
    except Exception:
        pe = 0

    return pe


def add_ps(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    psr = row.get("psr")
    try:
        ps = close_mean / psr
    except Exception:
        ps = 0

    return ps


def add_market_cap(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    total_share = row.get("total_share")
    try:
        market_cap = (close_mean * total_share) / RIAL_TO_BILLION_TOMAN
    except Exception:
        market_cap = 0

    return market_cap


def add_last_update(row):

    last_update = str(row.get("last_time"))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def stock_option_value_change_main():

    instrument_info = get_instrument_info()
    instrument_info = instrument_info[
        [
            "ins_code",
            "symbol",
            "name",
            "sector_pe",
            "eps",
            "psr",
            "total_share",
            "month_mean_volume",
        ]
    ]
    option_types = [CALL_OPTION, PUT_OPTION]
    for option_type in option_types:
        options = get_last_options(option_type)

        if options.empty:
            return

        left_on = "call_ins_code"
        if option_type == PUT_OPTION:
            left_on = "put_ins_code"
        options = pd.merge(
            left=options,
            right=instrument_info,
            left_on=left_on,
            right_on="ins_code",
            how="left",
        )

        options.dropna(inplace=True)
        options = get_asset_options_value_change(
            options=options, option_type=option_type
        )
        options = options[options["value_change"] != 0]

        options = pd.merge(left=options, right=instrument_info, on="symbol", how="left")
        options = options[
            [
                "ins_code",
                "symbol",
                "name",
                "last_mean",
                "month_mean",
                "value_change",
                "total_share",
                "sector_pe",
                "psr",
                "eps",
            ]
        ]

        last_data = get_market_watch_data_from_redis()

        last_data["daily_roi"] = (
            last_data["last_price_change"] / last_data["yesterday_price"]
        ) * 100
        last_data = last_data[["ins_code", "closing_price", "daily_roi", "last_time"]]
        options = pd.merge(left=options, right=last_data, on="ins_code", how="left")

        options["link"] = options.apply(add_link, axis=1)
        options["pe"] = options.apply(add_pe, axis=1)
        options["ps"] = options.apply(add_ps, axis=1)
        options["market_cap"] = options.apply(add_market_cap, axis=1)
        options.dropna(inplace=True)
        options["last_time"] = options["last_time"].astype(int)
        options["last_update"] = options.apply(add_last_update, axis=1)
        options = options.to_dict(orient="records")

        if options:
            if option_type == CALL_OPTION:
                collection_name = "call_value_change"
            elif option_type == PUT_OPTION:
                collection_name = "put_value_change"
            else:
                continue

            mongo_client = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name=collection_name
            )
            mongo_client.insert_docs_into_collection(documents=options)


@task_timing
@shared_task(name="stock_option_value_change_task")
def stock_option_value_change(run_mode: str = AUTO_MODE):

    # if run_mode == MANUAL_MODE or is_scheduled(
    #     weekdays=[0, 1, 2, 3, 4], start_hour=8, end_hour=19
    # ):
    print(Fore.BLUE + "Checking stock options value change ..." + Style.RESET_ALL)
    stock_option_value_change_main()
    print(Fore.GREEN + "Stock options value change updated" + Style.RESET_ALL)
