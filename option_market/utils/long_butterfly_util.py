from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN, OPTION_REDIS_DB

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    CALL_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)
from colorama import Fore, Style


redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def add_profits(
    coordinates, profit_factor, remained_day, base_equity_last_price, mid_strike
):
    if base_equity_last_price != 0:
        required_change = (
            (mid_strike - base_equity_last_price) / base_equity_last_price
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

    for coordinate in coordinates:
        if coordinate["x_2"] == mid_strike:
            net_profit = coordinate["y_2"]

    if profit_factor != 0:
        profits["final_profit"] = (net_profit / profit_factor) * 100

    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits


def long_butterfly(option_data):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_sell_price"] > 0)
        & (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="long_butterfly", ncols=10
    ):
        cartesians = CartesianProduct(dataframe=end_date_option, iterations=2)
        cartesians = cartesians.get_cartesian_product()
        if len(cartesians) >= 2:
            for _, row in cartesians[1].iterrows():
                add_option = AddOption()

                low_strike = float(row.get("strike_price_2"))
                low_premium = end_date_option[
                    end_date_option["strike_price"] == low_strike
                ]
                low_premium = float(low_premium.get("call_best_sell_price").iloc[0])
                add_option.add_call_buy(strike=low_strike, premium=low_premium)

                mid_strike = float(row.get("strike_price_1"))
                mid_premium = end_date_option[
                    end_date_option["strike_price"] == mid_strike
                ]
                mid_premium = float(mid_premium.get("call_best_buy_price").iloc[0])
                add_option.add_call_sell(strike=mid_strike, premium=mid_premium)
                add_option.add_call_sell(strike=mid_strike, premium=mid_premium)

                high_strike = float(row.get("strike_price_0"))
                high_premium = end_date_option[
                    end_date_option["strike_price"] == high_strike
                ]
                high_premium = float(high_premium.get("call_best_sell_price").iloc[0])
                add_option.add_call_buy(strike=high_strike, premium=high_premium)

                option_list = add_option.get_option_list
                strategy = Strategy(option_list=option_list, name="long_butterfly")

                coordinates = strategy.get_coordinate()

                low_call_buy = end_date_option.loc[
                    end_date_option["strike_price"] == low_strike
                ].iloc[0]

                mid_call_sell = end_date_option.loc[
                    end_date_option["strike_price"] == mid_strike
                ].iloc[0]

                high_call_buy = end_date_option.loc[
                    end_date_option["strike_price"] == high_strike
                ].iloc[0]

                profit_factor = -1 * (low_premium + high_premium) + 2 * mid_premium
                remained_day = row.get("remained_day")
                base_equity_last_price = row.get("base_equity_last_price")
                document = {
                    "id": uuid4().hex,
                    "base_equity_symbol": row.get("base_equity_symbol"),
                    "base_equity_last_price": base_equity_last_price,
                    "call_buy_symbol_low": low_call_buy.get("call_symbol"),
                    "call_best_sell_price_low": low_premium,
                    "call_buy_strike_low": low_strike,
                    "call_buy_value_low": low_call_buy.get("call_value")
                    / RIAL_TO_BILLION_TOMAN,
                    "call_sell_symbol_mid": mid_call_sell.get("call_symbol"),
                    "call_best_buy_price_mid": mid_premium,
                    "call_sell_strike_mid": mid_strike,
                    "call_sell_value_mid": mid_call_sell.get("call_value")
                    / RIAL_TO_BILLION_TOMAN,
                    "call_buy_symbol_high": high_call_buy.get("call_symbol"),
                    "call_best_sell_price_high": high_premium,
                    "call_buy_strike_high": high_strike,
                    "call_buy_value_high": high_call_buy.get("call_value")
                    / RIAL_TO_BILLION_TOMAN,
                    **add_profits(
                        coordinates,
                        abs(profit_factor),
                        remained_day,
                        base_equity_last_price,
                        mid_strike,
                    ),
                    "end_date": row.get("end_date"),
                    "profit_factor": profit_factor,
                    "coordinates": coordinates,
                    "actions": [
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{low_call_buy.get("call_ins_code")}",
                            **add_action_detail(low_call_buy, CALL_BUY_COLUMN_MAPPING),
                            **add_option_fees(low_call_buy),
                        },
                        {
                            "action": "فروش",
                            "link": f"https://www.tsetmc.com/instInfo/{mid_call_sell.get("call_ins_code")}",
                            **add_action_detail(
                                mid_call_sell, CALL_SELL_COLUMN_MAPPING
                            ),
                            **add_option_fees(mid_call_sell),
                        },
                        {
                            "action": "فروش",
                            "link": f"https://www.tsetmc.com/instInfo/{mid_call_sell.get("call_ins_code")}",
                            **add_action_detail(
                                mid_call_sell, CALL_SELL_COLUMN_MAPPING
                            ),
                            **add_option_fees(mid_call_sell),
                        },
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{high_call_buy.get("call_ins_code")}",
                            **add_action_detail(high_call_buy, CALL_BUY_COLUMN_MAPPING),
                            **add_option_fees(high_call_buy),
                        },
                    ],
                }

                result.append(document)

    print(Fore.GREEN + f"long_butterfly, {len(result)} records." + Style.RESET_ALL)

    redis_conn.bulk_push_list_of_dicts(list_key="long_butterfly", list_of_dicts=result)
