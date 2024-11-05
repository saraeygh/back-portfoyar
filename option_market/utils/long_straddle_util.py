from uuid import uuid4
from tqdm import tqdm
from core.configs import RIAL_TO_BILLION_TOMAN
from . import (
    AddOption,
    Strategy,
    CALL_BUY_COLUMN_MAPPING,
    PUT_BUY_COLUMN_MAPPING,
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
    *list(CALL_BUY_COLUMN_MAPPING.values()),
    "put_value",
    *list(PUT_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def long_straddle(option_data, redis_conn):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_sell_price"] > 0)
        & (option_data["put_best_sell_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["put_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="long_straddle", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_sell_price"))
            put_premium = float(row.get("put_best_sell_price"))

            add_option = AddOption()
            add_option.add_call_buy(strike=strike_price, premium=call_premium)
            add_option.add_put_buy(strike=strike_price, premium=put_premium)

            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="long_straddle")
            coordinates = strategy.get_coordinate()

            profit_factor = -1 * (call_premium + put_premium)
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": row.get("base_equity_last_price"),
                "call_buy_symbol": row.get("call_symbol"),
                "call_best_sell_price": call_premium,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                "strike_price": strike_price,
                "remained_day": row.get("remained_day"),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "call_ins_code"),
                        **add_action_detail(row, CALL_BUY_COLUMN_MAPPING),
                    },
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "put_ins_code"),
                        **add_action_detail(row, PUT_BUY_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"long_straddle, {len(result)} records." + Style.RESET_ALL)
    if result:
        redis_conn.bulk_push_list_of_dicts(
            list_key="long_straddle", list_of_dicts=result
        )
