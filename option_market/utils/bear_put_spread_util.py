from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    PUT_BUY_COLUMN_MAPPING,
    PUT_SELL_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=3)


def add_profits(coordinates, profit_factor, remained_day, base_equity_last_price, low_strike):
    if base_equity_last_price != 0 and base_equity_last_price > low_strike:
        required_change = (
            (low_strike - base_equity_last_price) / base_equity_last_price
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

    net_profit = coordinates[0]["y_1"]
    if profit_factor != 0:
        profits["final_profit"] = (net_profit / profit_factor) * 100

    return profits


def bear_put_spread():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["put_best_buy_price"] > 0)
        & (distinct_end_date_options["put_best_sell_price"] > 0)
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
        distinct_end_date_options, desc="bear_put_spread", ncols=10
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
                high_premium = float(high_premium.get("put_best_sell_price").iloc[0])
                add_option.add_put_buy(strike=high_strike, premium=high_premium)

                option_list = add_option.get_option_list
                strategy = Strategy(option_list=option_list, name="bull_put_spread")

                coordinates = strategy.get_coordinate()

                buy_row = end_date_option.loc[
                    end_date_option["strike_price"] == high_strike
                ].iloc[0]

                sell_row = end_date_option.loc[
                    end_date_option["strike_price"] == low_strike
                ].iloc[0]

                remained_day = row.get("remained_day")
                profit_factor = -1 * high_premium + low_premium
                base_equity_last_price = row.get("base_equity_last_price")
                document = {
                    "id": uuid4().hex,

                    "base_equity_symbol": row.get("base_equity_symbol"),
                    "base_equity_last_price": base_equity_last_price,

                    "put_buy_symbol": buy_row.get("put_symbol"),
                    "put_best_sell_price": high_premium,
                    "put_buy_strike": high_strike,
                    "put_buy_value": buy_row.get("put_value") / RIAL_TO_BILLION_TOMAN,

                    "put_sell_symbol": sell_row.get("put_symbol"),
                    "put_best_buy_price": low_premium,
                    "put_sell_strike": low_strike,
                    "put_sell_value": buy_row.get("put_value") / RIAL_TO_BILLION_TOMAN,

                    **add_profits(coordinates, abs(profit_factor), remained_day, base_equity_last_price, low_strike),

                    "profit_factor": profit_factor,

                    "coordinates": coordinates,

                    "actions": [
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{buy_row.get("put_ins_code")}",
                            **add_action_detail(buy_row, PUT_BUY_COLUMN_MAPPING),
                            **add_option_fees(buy_row)
                        },
                        {
                            "action": "فروش",
                            "link": f"https://www.tsetmc.com/instInfo/{sell_row.get("put_ins_code")}",
                            **add_action_detail(sell_row, PUT_SELL_COLUMN_MAPPING),
                            **add_option_fees(sell_row)
                        },
                    ],
                }

                result.append(document)

    print(f"bear_put_spread, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="bear_put_spread", list_of_dicts=result)
