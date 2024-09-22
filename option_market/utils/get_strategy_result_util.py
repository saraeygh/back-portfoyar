import pandas as pd
from core.utils import RedisInterface

COLUMN_ORDER = {
    "long_calls": [
        "symbol",
        "strike",
        "asset_name",
        "base_equit_price",
        "break_even_percent",
        "days_to_expire",
        "last_update",
        "expiration_date",
        "monthly_final_profit_percent",
        "leverage",
        "best_sell_price",
        "best_buy_volume",
        "best_sell_volume",
        "volume",
        "number",
        "value",
        "link",
        "option_type",
    ],
    "covered_calls": [
        "symbol",
        "strike",
        "asset_name",
        "base_equit_price",
        "final_profit_percent",
        "days_to_expire",
        "break_even",
        "monthly_final_profit_percent",
        "annual_final_profit_percent",
        "last_update",
        "expiration_date",
        "best_buy_price",
        "option_type",
        "best_buy_volume",
        "best_sell_volume",
        "volume",
        "number",
        "value",
        "link",
    ],
}

empty_df = pd.DataFrame()


def get_long_calls_result(option_list: pd.DataFrame):
    if option_list.empty:
        return empty_df

    option_list = option_list[COLUMN_ORDER.get("long_calls")]
    option_list = option_list.sort_values(
        by="monthly_final_profit_percent", ascending=False
    )
    option_list["option_type"] = "اختیار خرید"

    return option_list


def get_covered_calls_result(option_list):
    if option_list.empty:
        return empty_df

    option_list = option_list[COLUMN_ORDER.get("covered_calls")]
    option_list = option_list.sort_values(
        by="monthly_final_profit_percent", ascending=False
    )
    option_list["option_type"] = "اختیار خرید"

    return option_list


def get_strategy_result(collection_key):

    redis_conn = RedisInterface(db=3)
    option_list = redis_conn.get_list_of_dicts(list_key=collection_key)
    option_list = pd.DataFrame(option_list)

    if collection_key == "long_calls":
        result = get_long_calls_result(option_list)
    elif collection_key == "covered_calls":
        result = get_covered_calls_result(option_list)
    else:
        result = empty_df

    return result
