from celery import shared_task
from core.utils import RedisInterface, task_timing

import pandas as pd
from core.models import FeatureToggle, ACTIVE

from core.configs import OPTION_REDIS_DB
from core.utils import get_http_response, replace_arabic_letters_pd, MARKET_STATE
from stock_market.utils import (
    MAIN_MARKET_TYPE_DICT,
    TSETMC_REQUEST_HEADERS,
    get_last_market_watch_data,
    get_market_state,
)

from option_market.utils import (
    COMMON_OPTION_COLUMN,
    BASE_EQUITY_COLUMNS,
    CALL_OPTION_COLUMN,
    PUT_OPTION_COLUMN,
    populate_all_option_strategy,
)
from colorama import Fore, Style

redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def add_base_equity_best_orders(row, order_index):
    best_order = row.get("blDs")
    best_order = best_order[0]

    return best_order[order_index]


def edit_last_update(row):
    last_update = str(int(row.get("last_update")))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def add_link(row) -> str:
    inst_id = str(row["inst_id"])
    inst_link = f"https://main.tsetmc.com/InstInfo/{inst_id}/"

    return inst_link


@task_timing
@shared_task(name="update_option_data_from_tse_task")
def update_option_data_from_tse():
    check_market_state = FeatureToggle.objects.get(name=MARKET_STATE)
    for market_type_num, _ in MAIN_MARKET_TYPE_DICT.items():
        if check_market_state.state == ACTIVE:
            market_state = get_market_state(market_type_num)
            if market_state != check_market_state.value:
                print(Fore.RED + "Market is closed." + Style.RESET_ALL)
                continue

        URL = "https://cdn.tsetmc.com/api/Instrument/GetInstrumentOptionMarketWatch/0"

        option_data = get_http_response(req_url=URL, req_headers=TSETMC_REQUEST_HEADERS)
        option_data = option_data.json()
        option_data = option_data.get("instrumentOptMarketWatch")
        option_data = pd.DataFrame(option_data)
        option_data = option_data.rename(columns=COMMON_OPTION_COLUMN)
        option_data = option_data.rename(columns=BASE_EQUITY_COLUMNS)
        option_data = option_data.rename(columns=CALL_OPTION_COLUMN)
        option_data = option_data.rename(columns=PUT_OPTION_COLUMN)

        option_data["base_equity_symbol"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("base_equity_symbol",)
        )
        option_data["call_name"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("call_name",)
        )
        option_data["call_symbol"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("call_symbol",)
        )
        option_data["put_symbol"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("put_symbol",)
        )
        option_data["put_name"] = option_data.apply(
            replace_arabic_letters_pd, axis=1, args=("put_name",)
        )

        last_market_watch_data = get_last_market_watch_data(show_traded="false")

        base_equity_data = last_market_watch_data.copy(deep=True)
        base_equity_data = base_equity_data.rename(
            columns={
                "insCode": "base_equity_ins_code",
                "lvc": "base_equity_name",
                "pdv": "base_equity_last_price",
                "hEven": "base_equity_last_update",
                "qtc": "base_equity_value",
            }
        )
        base_equity_data["base_equity_best_buy_price"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("pmd",), axis=1
        )
        base_equity_data["base_equity_best_sell_price"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("pmo",), axis=1
        )
        base_equity_data["base_equity_best_buy_volume"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("qmd",), axis=1
        )
        base_equity_data["base_equity_best_sell_volume"] = base_equity_data.apply(
            add_base_equity_best_orders, args=("qmo",), axis=1
        )

        base_equity_data = base_equity_data[
            [
                "base_equity_ins_code",
                "base_equity_name",
                "base_equity_value",
                "base_equity_last_price",
                "base_equity_best_buy_price",
                "base_equity_best_sell_price",
                "base_equity_best_buy_volume",
                "base_equity_best_sell_volume",
                "base_equity_last_update",
            ]
        ]

        option_data = pd.merge(
            left=option_data,
            right=base_equity_data,
            on="base_equity_ins_code",
            how="left",
        )

        option_data.dropna(inplace=True)

        call_data = last_market_watch_data.copy(deep=True)
        call_data = call_data.rename(
            columns={"insCode": "call_ins_code", "hEven": "call_last_update"}
        )
        call_data = call_data[["call_ins_code", "call_last_update"]]
        option_data = pd.merge(
            left=option_data, right=call_data, on="call_ins_code", how="left"
        )

        put_data = last_market_watch_data.copy(deep=True)
        put_data = put_data.rename(
            columns={"insCode": "put_ins_code", "hEven": "put_last_update"}
        )
        put_data = put_data[["put_ins_code", "put_last_update"]]
        option_data = pd.merge(
            left=option_data, right=put_data, on="put_ins_code", how="left"
        )

        option_data.fillna(value=60000, inplace=True)
        option_data["call_last_update"] = option_data["call_last_update"].astype(int)
        option_data["put_last_update"] = option_data["put_last_update"].astype(int)

        option_data = option_data.to_dict(orient="records")
        redis_conn.bulk_push_list_of_dicts(
            list_key="option_data", list_of_dicts=option_data
        )
        print(Fore.BLUE + f"option_data, {len(option_data)} records." + Style.RESET_ALL)

        populate_all_option_strategy()

        return
