from uuid import uuid4
from tqdm import tqdm
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    CoveredCall,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
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
    "base_equity_last_price",
    *list(BASE_EQUITY_BUY_COLUMN_MAPPING.values()),
]


def add_profits(row):
    remained_day = row.get("remained_day")
    strike_price = float(row.get("strike_price"))
    call_premium = float(row.get("call_best_buy_price"))
    base_equity_last_price = float(row.get("base_equity_last_price"))

    if base_equity_last_price != 0 and base_equity_last_price < strike_price:
        required_change = (
            (strike_price - base_equity_last_price) / base_equity_last_price
        ) * 100
    else:
        required_change = 0

    profits = {
        "final_profit": 0,
        "required_change": required_change,
        "remained_day": remained_day,
        "monthly_profit": 0,
        "yearly_profit": 0,
    }

    if base_equity_last_price != call_premium:
        profits["final_profit"] = (
            (strike_price / (base_equity_last_price - call_premium)) - 1
        ) * 100

    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits


def covered_call(option_data, redis_conn):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["base_equity_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="covered_call", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
        for _, row in end_date_option.iterrows():
            strike = float(row.get("strike_price"))
            premium = float(row.get("call_best_buy_price"))
            asset_price = float(row.get("base_equity_last_price"))

            covered_call_strategy = CoveredCall(
                strike=strike, premium=premium, asset_price=asset_price
            )
            coordinates = covered_call_strategy.get_coordinate()

            profit_factor = premium - asset_price
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": asset_price,
                "base_equity_best_sell_price": row.get("base_equity_best_sell_price"),
                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": premium,
                "strike_price": strike,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                **add_profits(row),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "coordinates": coordinates,
                "actions": [
                    {
                        "link": get_link_str(row, "base_equity_ins_code"),
                        "action": "خرید",
                        **add_action_detail(row, BASE_EQUITY_BUY_COLUMN_MAPPING),
                    },
                    {
                        "link": get_link_str(row, "call_ins_code"),
                        "action": "فروش",
                        **add_action_detail(row, CALL_SELL_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"covered_call, {len(result)} records." + Style.RESET_ALL)

    redis_conn.bulk_push_list_of_dicts(list_key="covered_call", list_of_dicts=result)
