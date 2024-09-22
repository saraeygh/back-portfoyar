from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    CALL_SELL_COLUMN_MAPPING,
    PUT_SELL_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)

redis_conn = RedisInterface(db=3)


def add_profits(coordinates, profit_factor, remained_day):
    profits = {
        "final_profit": 0,
        "monthly_profit": 0,
        "yearly_profit": 0,
    }

    if len(coordinates) == 5:
        net_profit = coordinates[2]["y_2"]
    else:
        net_profit = coordinates[1]["y_2"]

    if profit_factor != 0:
        profits["final_profit"] = (net_profit / profit_factor) * 100

    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits


def short_strangle():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["put_best_buy_price"] > 0)
        & (distinct_end_date_options["call_best_buy_price"] > 0)
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
        distinct_end_date_options, desc="short_strangle", ncols=10
    ):
        cartesians = CartesianProduct(dataframe=end_date_option)
        cartesians = cartesians.get_cartesian_product()

        if cartesians:
            for _, row in cartesians[0].iterrows():
                add_option = AddOption()

                low_strike = float(row.get("strike_price_1"))
                low_premium = end_date_option[
                    end_date_option["strike_price"] == low_strike
                ]
                low_premium = float(low_premium.get("put_best_buy_price").iloc[0])
                add_option.add_put_sell(strike=low_strike, premium=low_premium)

                high_strike = float(row.get("strike_price_0"))
                high_premium = end_date_option[
                    end_date_option["strike_price"] == high_strike
                ]
                high_premium = float(high_premium.get("call_best_buy_price").iloc[0])
                add_option.add_call_sell(strike=high_strike, premium=high_premium)

                option_list = add_option.get_option_list
                strategy = Strategy(option_list=option_list, name="short_strangle")

                coordinates = strategy.get_coordinate()

                put_sell_row = end_date_option.loc[
                    end_date_option["strike_price"] == low_strike
                ].iloc[0]

                call_sell_row = end_date_option.loc[
                    end_date_option["strike_price"] == high_strike
                ].iloc[0]

                profit_factor = low_premium + high_premium
                remained_day = row.get("remained_day")
                document = {
                    "id": uuid4().hex,

                    "base_equity_symbol": row.get("base_equity_symbol"),
                    "base_equity_value": row.get("base_equity_value") / RIAL_TO_BILLION_TOMAN,
                    "base_equity_last_price": row.get("base_equity_last_price"),

                    "put_sell_symbol": put_sell_row.get("put_symbol"),
                    "put_sell_strike": low_strike,
                    "put_sell_notional_value": put_sell_row.get("put_notional_value") / RIAL_TO_BILLION_TOMAN,

                    "call_sell_symbol": call_sell_row.get("call_symbol"),
                    "call_sell_strike": high_strike,
                    "call_sell_notional_value": call_sell_row.get("call_notional_value") / RIAL_TO_BILLION_TOMAN,

                    "remained_day": remained_day,

                    **add_profits(coordinates, abs(profit_factor), remained_day),

                    "profit_factor": profit_factor,

                    "coordinates": coordinates,

                    "actions": [
                        {
                            "action": "فروش",
                            "link": f"https://www.tsetmc.com/instInfo/{put_sell_row.get("put_ins_code")}",
                            **add_action_detail(put_sell_row, PUT_SELL_COLUMN_MAPPING),
                            **add_option_fees(put_sell_row)
                        },
                        {
                            "action": "فروش",
                            "link": f"https://www.tsetmc.com/instInfo/{call_sell_row.get("call_ins_code")}",
                            **add_action_detail(call_sell_row, CALL_SELL_COLUMN_MAPPING),
                            **add_option_fees(call_sell_row)
                        },
                    ],
                }

                result.append(document)

    print(f"short_strangle, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="short_strangle", list_of_dicts=result)
