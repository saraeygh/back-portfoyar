from celery import shared_task
import pandas as pd
from core.configs import STOCK_OPTION_STRIKE_DEVIATION, STOCK_DB, OPTION_REDIS_DB
from core.utils import RedisInterface, task_timing, MongodbInterface, MARKET_STATE
from core.models import FeatureToggle, ACTIVE

from option_market.utils import (
    COMMON_OPTION_COLUMN,
    BASE_EQUITY_COLUMNS,
    CALL_OPTION_COLUMN,
    PUT_OPTION_COLUMN,
)
from stock_market.utils import (
    MAIN_MARKET_TYPE_DICT,
    CALL_OPTION,
    PUT_OPTION,
    get_market_state,
)

from colorama import Fore, Style

redis_conn = RedisInterface(db=OPTION_REDIS_DB)

CALL_OLD_NEW_MAPPING = {
    "call_ins_code": "inst_id",
    "option_link": "option_link",
    "stock_link": "stock_link",
    "base_equity_last_update": "last_update",
    "call_symbol": "symbol",
    "base_equity_symbol": "asset_name",
    "base_equity_last_price": "base_equit_price",
    "strike_price": "strike",
    "monthly_price_spread": "monthly_price_spread",
    "remained_day": "days_to_expire",
    "price_spread": "price_spread",
    "end_date": "expiration_date",
    "option_type": "option_type",
    "call_value": "value",
    "call_best_sell_price": "premium",
    "strike_premium": "strike_premium",
    "strike_deviation": "strike_deviation",
}

PUT_OLD_NEW_MAPPING = {
    "put_ins_code": "inst_id",
    "option_link": "option_link",
    "stock_link": "stock_link",
    "base_equity_last_update": "last_update",
    "put_symbol": "symbol",
    "base_equity_symbol": "asset_name",
    "base_equity_last_price": "base_equit_price",
    "strike_price": "strike",
    "monthly_price_spread": "monthly_price_spread",
    "remained_day": "days_to_expire",
    "price_spread": "price_spread",
    "end_date": "expiration_date",
    "option_type": "option_type",
    "put_value": "value",
    "put_best_buy_price": "premium",
    "strike_premium": "strike_premium",
    "strike_deviation": "strike_deviation",
}


def get_last_options():
    last_options = pd.DataFrame(redis_conn.get_list_of_dicts(list_key="option_data"))
    return last_options


def strike_deviation(row):
    strike = int(row.get("strike_price"))
    asset_price = int(row.get("base_equity_last_price"))

    try:
        deviation = ((strike - asset_price) / asset_price) * 100
    except Exception:
        deviation = 0

    return deviation


def add_strike_premium(row, option_type):
    strike = int(row.get("strike_price"))
    if option_type == CALL_OPTION:
        premium = int(row.get("call_best_sell_price"))
    else:
        premium = int(row.get("put_best_buy_price"))

    return strike + premium


def add_price_spread(row, option_type):
    strike_premium = int(row.get("strike_premium"))
    asset_price = int(row.get("base_equity_last_price"))

    try:
        spread = (((strike_premium) - asset_price) / asset_price) * 100
    except Exception:
        spread = 0

    return spread


def monthly_price_spread(row):
    remained_days = int(row.get("remained_day"))
    price_spread = int(row.get("price_spread"))

    try:
        monthly_spread = (price_spread / remained_days) * 30
    except Exception:
        monthly_spread = 0

    return monthly_spread


def add_stock_link(row):
    ins_code = str(row.get(" base_equity_ins_code"))
    link = f"https://main.tsetmc.com/InstInfo/{ins_code}/"

    return link


def add_option_link(row, option_type):
    if option_type == CALL_OPTION:
        ins_code = str(row.get("call_ins_code"))
    else:
        ins_code = str(row.get("put_ins_code"))
    link = f"https://main.tsetmc.com/InstInfo/{ins_code}/"

    return link


def get_call_spreads(spreads):
    spreads = spreads[
        list(COMMON_OPTION_COLUMN.values())
        + list(BASE_EQUITY_COLUMNS.values())
        + list(CALL_OPTION_COLUMN.values())
        + ["call_last_update", "base_equity_last_update"]
    ]
    spreads = spreads.loc[
        (spreads["call_last_update"] > 90000)
        & (spreads["base_equity_last_update"] > 90000)
    ]

    spreads["strike_deviation"] = spreads.apply(strike_deviation, axis=1)
    spreads = spreads[abs(spreads["strike_deviation"]) < STOCK_OPTION_STRIKE_DEVIATION]

    if not spreads.empty:
        spreads["strike_premium"] = spreads.apply(
            add_strike_premium, axis=1, args=(CALL_OPTION,)
        )

        spreads["price_spread"] = spreads.apply(
            add_price_spread, axis=1, args=(CALL_OPTION,)
        )

        spreads["monthly_price_spread"] = spreads.apply(monthly_price_spread, axis=1)

        spreads["stock_link"] = spreads.apply(add_stock_link, axis=1)
        spreads["option_link"] = spreads.apply(
            add_option_link, axis=1, args=(CALL_OPTION,)
        )

        spreads["option_type"] = "اختیار خرید"

        spreads.dropna(inplace=True)
        spreads = spreads.rename(columns=CALL_OLD_NEW_MAPPING)
        spreads = spreads[list(CALL_OLD_NEW_MAPPING.values())]
        spreads = spreads.to_dict(orient="records")
    else:
        spreads = pd.DataFrame()
        spreads = spreads.to_dict(orient="records")

    return spreads


def get_put_spreads(spreads):
    spreads = spreads[
        list(COMMON_OPTION_COLUMN.values())
        + list(BASE_EQUITY_COLUMNS.values())
        + list(PUT_OPTION_COLUMN.values())
        + ["put_last_update", "base_equity_last_update"]
    ]
    spreads = spreads.loc[
        (spreads["put_last_update"] > 90000)
        & (spreads["base_equity_last_update"] > 90000)
    ]

    spreads["strike_deviation"] = spreads.apply(strike_deviation, axis=1)
    spreads = spreads[abs(spreads["strike_deviation"]) < STOCK_OPTION_STRIKE_DEVIATION]

    if not spreads.empty:
        spreads["strike_premium"] = spreads.apply(
            add_strike_premium, axis=1, args=(PUT_OPTION,)
        )

        spreads["price_spread"] = spreads.apply(
            add_price_spread, axis=1, args=(PUT_OPTION,)
        )

        spreads["monthly_price_spread"] = spreads.apply(monthly_price_spread, axis=1)

        spreads["stock_link"] = spreads.apply(add_stock_link, axis=1)
        spreads["option_link"] = spreads.apply(
            add_option_link, axis=1, args=(PUT_OPTION,)
        )

        spreads["option_type"] = "اختیار فروش"

        spreads.dropna(inplace=True)
        spreads = spreads.rename(columns=PUT_OLD_NEW_MAPPING)
        spreads = spreads[list(PUT_OLD_NEW_MAPPING.values())]
        spreads = spreads.to_dict(orient="records")
    else:
        spreads = pd.DataFrame()
        spreads = spreads.to_dict(orient="records")

    return spreads


@task_timing
@shared_task(name="stock_option_price_spread_task")
def stock_option_price_spread():

    print(Fore.BLUE + "Checking stock price spread ..." + Style.RESET_ALL)
    check_market_state = FeatureToggle.objects.get(name=MARKET_STATE)
    for market_type in list(MAIN_MARKET_TYPE_DICT.keys()):
        if check_market_state.state == ACTIVE:
            market_state = get_market_state(market_type)
            if market_state != check_market_state.value:
                print(Fore.RED + "market is closed!" + Style.RESET_ALL)
                continue

        spreads = get_last_options()
        spreads_list = list()
        if not spreads.empty:
            call_spreads = get_call_spreads(spreads)
            put_spreads = get_put_spreads(spreads)

        else:
            spreads = pd.DataFrame()
            spreads = spreads.to_dict(orient="records")

        spreads_list = call_spreads + put_spreads
        if spreads_list:
            mongo_client = MongodbInterface(
                db_name=STOCK_DB, collection_name="option_price_spread"
            )
            mongo_client.insert_docs_into_collection(documents=spreads_list)

            return
