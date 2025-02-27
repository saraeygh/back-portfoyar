from uuid import uuid4
from tqdm import tqdm

from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import RedisInterface, get_deviation_percent

from . import (
    AddOption,
    Strategy,
    CALL_BUY_COLUMN_MAPPING,
    get_distinc_end_date_options,
    add_details,
    filter_rows_with_nan_values,
    get_link_str,
    get_fee_percent,
)


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "call_value",
    *list(CALL_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
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
        "fee": 0,
    }
    break_even = get_fee_percent(
        break_even,
        strike_sum=strike_price,
        premium_sum=call_premium,
        net_pay=call_premium,
    )

    try:
        break_even["final_break_even"] = get_deviation_percent(
            strike_price + call_premium, base_equity_last_price
        )
        break_even["leverage"] = base_equity_last_price / call_premium

        if remained_day != 0:
            break_even["monthly_break_even"] = (
                break_even["final_break_even"] / remained_day
            ) * 30
            break_even["yearly_break_even"] = break_even["monthly_break_even"] * 12

        return break_even

    except Exception:
        return break_even


def long_call(option_data, redis_db_num: int):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_sell_price"] > 0)
        & (option_data["call_last_update"] > 90000)
    ]
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["call_best_sell_price"] > 0)
        & (distinct_end_date_options["call_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="long_call", ncols=10):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_sell_price"))

            add_option = AddOption()
            add_option.add_call_buy(strike=strike_price, premium=call_premium)
            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="long_call")
            coordinates = strategy.get_coordinate()

            profit_factor = -1 * call_premium
            base_equity_last_price = row.get("base_equity_last_price")
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_order_book": row.get("base_equity_order_book"),
                "call_buy_symbol": row.get("call_symbol"),
                "call_best_sell_price": call_premium,
                "strike_price": strike_price,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                **add_break_even(row),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike_price / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "call_ins_code"),
                        **add_details(row, CALL_BUY_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"long_call, {len(result)} records." + Style.RESET_ALL)
    if result:
        redis_conn = RedisInterface(db=redis_db_num)
        redis_conn.bulk_push_list_of_dicts(list_key="long_call", list_of_dicts=result)
