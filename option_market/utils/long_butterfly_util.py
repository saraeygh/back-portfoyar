from uuid import uuid4
from tqdm import tqdm
from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import MongodbInterface, get_deviation_percent

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    CALL_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    get_distinc_end_date_options,
    add_details,
    filter_rows_with_nan_values,
    get_link_str,
)


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "call_value",
    *list(CALL_SELL_COLUMN_MAPPING.values()),
    *list(CALL_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def add_profits(
    coordinates, profit_factor, remained_day, base_equity_last_price, mid_strike
):
    if base_equity_last_price != 0:
        required_change = get_deviation_percent(mid_strike, base_equity_last_price)
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


def long_butterfly(option_data, mongo_db: str):
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
        distinct_end_date_options, desc="long_butterfly", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue

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
                    "base_equity_order_book": row.get("base_equity_order_book"),
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
                    "strike_price_deviation": max(
                        ((low_strike / base_equity_last_price) - 1),
                        ((mid_strike / base_equity_last_price) - 1),
                        ((high_strike / base_equity_last_price) - 1),
                    ),
                    "coordinates": coordinates,
                    "actions": [
                        {
                            "action": "خرید",
                            "link": get_link_str(low_call_buy, "call_ins_code"),
                            **add_details(low_call_buy, CALL_BUY_COLUMN_MAPPING),
                        },
                        {
                            "action": "فروش",
                            "link": get_link_str(mid_call_sell, "call_ins_code"),
                            **add_details(mid_call_sell, CALL_SELL_COLUMN_MAPPING),
                        },
                        {
                            "action": "فروش",
                            "link": get_link_str(mid_call_sell, "call_ins_code"),
                            **add_details(mid_call_sell, CALL_SELL_COLUMN_MAPPING),
                        },
                        {
                            "action": "خرید",
                            "link": get_link_str(high_call_buy, "call_ins_code"),
                            **add_details(high_call_buy, CALL_BUY_COLUMN_MAPPING),
                        },
                    ],
                }

                result.append(document)

    print(Fore.GREEN + f"long_butterfly, {len(result)} records." + Style.RESET_ALL)
    if result:
        list_key = "long_butterfly"
        mongo_conn = MongodbInterface(db_name=mongo_db, collection_name=list_key)
        mongo_conn.insert_docs_into_collection(result)
