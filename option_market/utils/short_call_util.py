from uuid import uuid4
from tqdm import tqdm
from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import get_deviation_percent

from . import (
    AddOption,
    Strategy,
    CALL_SELL_COLUMN_MAPPING,
    get_distinc_end_date_options,
    add_action_detail,
    filter_rows_with_nan_values,
    get_link_str,
)
from colorama import Fore, Style


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "call_value",
    *list(CALL_SELL_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def add_profits(remained_day, base_equity_last_price, strike_price):
    if base_equity_last_price != 0 and base_equity_last_price > strike_price:
        required_change = get_deviation_percent(strike_price, base_equity_last_price)
    else:
        required_change = 0

    profits = {
        "final_profit": 100,
        "required_change": required_change,
        "remained_day": remained_day,
        "monthly_profit": "-",
        "yearly_profit": "-",
    }

    return profits


def short_call(option_data, redis_conn):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="short_call", ncols=10):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_buy_price"))

            add_option = AddOption()
            add_option.add_call_sell(strike=strike_price, premium=call_premium)
            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="short_call")
            coordinates = strategy.get_coordinate()

            remained_day = row.get("remained_day")
            profit_factor = call_premium
            base_equity_last_price = row.get("base_equity_last_price")
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_order_book": row.get("base_equity_order_book"),
                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": call_premium,
                "strike_price": strike_price,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                **add_profits(remained_day, base_equity_last_price, strike_price),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike_price / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "فروش",
                        "link": get_link_str(row, "call_ins_code"),
                        **add_action_detail(row, CALL_SELL_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"short_call, {len(result)} records." + Style.RESET_ALL)
    if result:
        redis_conn.bulk_push_list_of_dicts(list_key="short_call", list_of_dicts=result)
