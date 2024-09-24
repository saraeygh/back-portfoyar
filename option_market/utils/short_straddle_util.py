from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    AddOption,
    Strategy,
    CALL_SELL_COLUMN_MAPPING, PUT_SELL_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=3)


def add_profits(coordinates, profit_factor, remained_day, base_equity_last_price, strike_price):
    if base_equity_last_price != 0:
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

    if len(coordinates) == 4:
        net_profit = coordinates[1]["y_2"]
    else:
        net_profit = coordinates[0]["y_2"]

    if profit_factor != 0:
        profits["final_profit"] = (net_profit / profit_factor) * 100

    return profits


def short_straddle():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["call_best_buy_price"] > 0)
        & (distinct_end_date_options["put_best_buy_price"] > 0)
        & (distinct_end_date_options["call_last_update"] > 80000)
        & (distinct_end_date_options["put_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="short_straddle", ncols=10
    ):
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_buy_price"))
            put_premium = float(row.get("put_best_buy_price"))

            add_option = AddOption()
            add_option.add_call_sell(strike=strike_price, premium=call_premium)
            add_option.add_put_sell(strike=strike_price, premium=put_premium)

            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="short_straddle")
            coordinates = strategy.get_coordinate()

            profit_factor = call_premium + put_premium
            remained_day = row.get("remained_day")
            base_equity_last_price = row.get("base_equity_last_price")
            document = {
                "id": uuid4().hex,

                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,

                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": call_premium,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,

                "put_sell_symbol": row.get("put_symbol"),
                "put_best_buy_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,

                "strike_price": strike_price,

                **add_profits(coordinates, abs(profit_factor), remained_day, base_equity_last_price, strike_price),

                "profit_factor": profit_factor,

                "coordinates": coordinates,

                "actions": [
                    {
                        "action": "فروش",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("call_ins_code")}",
                        **add_action_detail(row, CALL_SELL_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                    {
                        "action": "فروش",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("put_ins_code")}",
                        **add_action_detail(row, PUT_SELL_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                ],
            }

            result.append(document)

    print(f"short_straddle, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="short_straddle", list_of_dicts=result)
