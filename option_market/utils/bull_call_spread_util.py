from uuid import uuid4
from tqdm import tqdm
from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import get_deviation_percent

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    CALL_BUY_COLUMN_MAPPING,
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
    *list(CALL_BUY_COLUMN_MAPPING.values()),
    *list(CALL_SELL_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def add_profits(
    coordinates, profit_factor, remained_day, base_equity_last_price, high_strike
):
    if base_equity_last_price != 0 and base_equity_last_price < high_strike:
        required_change = get_deviation_percent(high_strike, base_equity_last_price)
    else:
        required_change = 0

    profits = {
        "final_profit": 0,
        "required_change": required_change,
        "remained_day": remained_day,
        "monthly_profit": 0,
        "yearly_profit": 0,
    }

    net_profit = coordinates[-1]["y_1"]
    if profit_factor != 0:
        profits["final_profit"] = (net_profit / profit_factor) * 100

    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits


def bull_call_spread(option_data, redis_conn):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_sell_price"] > 0)
        & (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="bull_call_spread", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue

        cartesians = CartesianProduct(dataframe=end_date_option)
        cartesians = cartesians.get_cartesian_product()

        if cartesians:
            for _, row in cartesians[0].iterrows():
                remained_day = row.get("remained_day")

                add_option = AddOption()

                low_strike = float(row.get("strike_price_1"))
                low_premium = end_date_option[
                    end_date_option["strike_price"] == low_strike
                ]
                low_premium = float(low_premium.get("call_best_sell_price").iloc[0])
                add_option.add_call_buy(strike=low_strike, premium=low_premium)

                high_strike = float(row.get("strike_price_0"))
                high_premium = end_date_option[
                    end_date_option["strike_price"] == high_strike
                ]
                high_premium = float(high_premium.get("call_best_buy_price").iloc[0])
                add_option.add_call_sell(strike=high_strike, premium=high_premium)

                option_list = add_option.get_option_list
                strategy = Strategy(option_list=option_list, name="bull_call_spread")

                coordinates = strategy.get_coordinate()

                buy_row = end_date_option.loc[
                    end_date_option["strike_price"] == low_strike
                ].iloc[0]

                sell_row = end_date_option.loc[
                    end_date_option["strike_price"] == high_strike
                ].iloc[0]

                profit_factor = -1 * low_premium + high_premium
                base_equity_last_price = row.get("base_equity_last_price")
                document = {
                    "id": uuid4().hex,
                    "base_equity_symbol": row.get("base_equity_symbol"),
                    "base_equity_last_price": base_equity_last_price,
                    "call_buy_symbol": buy_row.get("call_symbol"),
                    "call_best_sell_price": low_premium,
                    "call_buy_strike": low_strike,
                    "call_buy_value": buy_row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                    "call_sell_symbol": sell_row.get("call_symbol"),
                    "call_best_buy_price": high_premium,
                    "call_sell_strike": high_strike,
                    "call_sell_value": sell_row.get("call_value")
                    / RIAL_TO_BILLION_TOMAN,
                    **add_profits(
                        coordinates,
                        abs(profit_factor),
                        remained_day,
                        base_equity_last_price,
                        high_strike,
                    ),
                    "end_date": row.get("end_date"),
                    "profit_factor": profit_factor,
                    "coordinates": coordinates,
                    "actions": [
                        {
                            "action": "خرید",
                            "link": get_link_str(buy_row, "call_ins_code"),
                            **add_action_detail(buy_row, CALL_BUY_COLUMN_MAPPING),
                        },
                        {
                            "action": "فروش",
                            "link": get_link_str(sell_row, "call_ins_code"),
                            **add_action_detail(sell_row, CALL_SELL_COLUMN_MAPPING),
                        },
                    ],
                }

                result.append(document)

    print(Fore.GREEN + f"bull_call_spread, {len(result)} records." + Style.RESET_ALL)

    redis_conn.bulk_push_list_of_dicts(
        list_key="bull_call_spread", list_of_dicts=result
    )
