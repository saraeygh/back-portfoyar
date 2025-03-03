from uuid import uuid4
from tqdm import tqdm
from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import MongodbInterface, get_deviation_percent


from . import (
    AddOption,
    Strategy,
    CALL_SELL_COLUMN_MAPPING,
    PUT_SELL_COLUMN_MAPPING,
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
    "put_value",
    *list(PUT_SELL_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def add_profits(
    coordinates, profit_factor, remained_day, base_equity_last_price, strike_price
):
    if base_equity_last_price != 0:
        required_change = get_deviation_percent(strike_price, base_equity_last_price)
    else:
        required_change = 0

    profits = {
        "final_profit": 0,
        "required_change": required_change,
        "remained_day": remained_day,
        "monthly_profit": "-",
        "yearly_profit": "-",
    }

    if len(coordinates) == 4:
        net_profit = coordinates[1]["y_2"]
    else:
        net_profit = coordinates[0]["y_2"]

    if profit_factor != 0:
        profits["final_profit"] = (net_profit / profit_factor) * 100

    return profits


def short_straddle(option_data, mongo_db: str):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["put_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["put_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="short_straddle", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
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
                "base_equity_order_book": row.get("base_equity_order_book"),
                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": call_premium,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                "put_sell_symbol": row.get("put_symbol"),
                "put_best_buy_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                "strike_price": strike_price,
                **add_profits(
                    coordinates,
                    abs(profit_factor),
                    remained_day,
                    base_equity_last_price,
                    strike_price,
                ),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike_price / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "فروش",
                        "link": get_link_str(row, "call_ins_code"),
                        **add_details(row, CALL_SELL_COLUMN_MAPPING),
                    },
                    {
                        "action": "فروش",
                        "link": get_link_str(row, "put_ins_code"),
                        **add_details(row, PUT_SELL_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"short_straddle, {len(result)} records." + Style.RESET_ALL)

    if result:
        list_key = "short_straddle"
        mongo_conn = MongodbInterface(db_name=mongo_db, collection_name=list_key)
        mongo_conn.insert_docs_into_collection(result)
