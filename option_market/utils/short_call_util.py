from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN, OPTION_REDIS_DB

from . import (
    AddOption,
    Strategy,
    CALL_SELL_COLUMN_MAPPING,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)
from colorama import Fore, Style


redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def add_profits(remained_day, base_equity_last_price, strike_price):
    if base_equity_last_price != 0 and base_equity_last_price > strike_price:
        required_change = (
            (strike_price - base_equity_last_price) / base_equity_last_price
        ) * 100
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


def short_call(option_data):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="short_call", ncols=10):
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
                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": call_premium,
                "strike_price": strike_price,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                **add_profits(remained_day, base_equity_last_price, strike_price),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "فروش",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("call_ins_code")}",
                        **add_action_detail(row, CALL_SELL_COLUMN_MAPPING),
                        **add_option_fees(row),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"short_call, {len(result)} records." + Style.RESET_ALL)

    redis_conn.bulk_push_list_of_dicts(list_key="short_call", list_of_dicts=result)
