from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN

from option_market.utils import (
    AddOption,
    Strategy,
    CALL_BUY_COLUMN_MAPPING,
    get_distinc_end_date_options,
    add_action_detail,
    filter_rows_with_nan_values,
)

redis_conn = RedisInterface(db=4)

REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "call_best_sell_price",
    "call_best_sell_volume",
    "call_last_update",
    "call_symbol",
    "call_value",
    #
    "base_equity_last_update",
    "base_equity_last_price",
    "base_equity_symbol",
    "base_equity_best_sell_price",
    "base_equity_best_sell_volume",
]


def add_break_even(row):
    remained_day = row.get("remained_day")
    strike_price = float(row.get("strike_price"))
    call_premium = float(row.get("call_best_sell_price"))
    base_equity_last_price = float(row.get("base_equity_last_price"))

    break_even = {
        "final_break_even": 0,
        "remained_day": remained_day,
        "monthly_break_even": 0,
        "yearly_break_even": 0,
        "leverage": 0,
    }

    try:
        break_even["final_break_even"] = (
            ((strike_price + call_premium) / base_equity_last_price) - 1
        ) * 100
        break_even["leverage"] = base_equity_last_price / call_premium

        if remained_day != 0:
            break_even["monthly_break_even"] = (
                break_even["final_break_even"] / remained_day
            ) * 30
            break_even["yearly_break_even"] = break_even["monthly_break_even"] * 12

        return break_even

    except Exception:
        return break_even


def long_call(option_data):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_sell_price"] > 0)
        & (option_data["call_last_update"] > 100000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="long_call", ncols=10):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_sell_price"))

            add_option = AddOption()
            add_option.add_call_buy(strike=strike_price, premium=call_premium)
            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="long_call")
            coordinates = strategy.get_coordinate()

            profit_factor = -1 * call_premium
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": row.get("base_equity_last_price"),
                "call_buy_symbol": row.get("call_symbol"),
                "call_best_sell_price": call_premium,
                "strike_price": strike_price,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                **add_break_even(row),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": "https://cdn.ime.co.ir/",
                        **add_action_detail(row, CALL_BUY_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(f"long_call, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="long_call", list_of_dicts=result)
