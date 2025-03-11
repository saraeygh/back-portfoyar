from uuid import uuid4
from tqdm import tqdm

from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import MongodbInterface, get_deviation_percent

from . import (
    MarriedPut,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
    PUT_BUY_COLUMN_MAPPING,
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
    "put_value",
    *list(PUT_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_last_price",
    *list(BASE_EQUITY_BUY_COLUMN_MAPPING.values()),
]


def add_break_even(row):
    remained_day = row.get("remained_day")
    put_premium = float(row.get("put_best_sell_price"))
    base_equity_last_price = float(row.get("base_equity_last_price"))

    break_even = {
        "final_break_even": 0,
        "remained_day": remained_day,
        "monthly_break_even": 0,
        "yearly_break_even": 0,
    }

    try:
        break_even["final_break_even"] = get_deviation_percent(
            base_equity_last_price + put_premium, base_equity_last_price
        )

        if remained_day != 0:
            break_even["monthly_break_even"] = (
                break_even["final_break_even"] / remained_day
            ) * 30
            break_even["yearly_break_even"] = break_even["monthly_break_even"] * 12

        return break_even

    except Exception:
        return break_even


def married_put(option_data, mongo_db: str):
    distinct_end_date_options = option_data.loc[
        (option_data["put_best_sell_price"] > 0)
        & (option_data["put_last_update"] > 90000)
        & (option_data["base_equity_last_update"] > 90000)
        & (option_data["strike_price"] <= option_data["base_equity_last_price"])
        & (option_data["strike_price"] >= 0.8 * option_data["base_equity_last_price"])
    ]

    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="married_put", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue

        for _, row in end_date_option.iterrows():
            strike = float(row.get("strike_price"))
            put_premium = float(row.get("put_best_sell_price"))
            base_equity_last_price = float(row.get("base_equity_last_price"))

            conversion_strategy = MarriedPut(
                strike=strike,
                put_premium=put_premium,
                asset_price=base_equity_last_price,
            )
            coordinates = conversion_strategy.get_coordinate()

            profit_factor = -1 * (put_premium + base_equity_last_price)
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_best_sell_price": row.get("base_equity_best_sell_price"),
                "base_equity_order_book": row.get("base_equity_order_book"),
                "strike_price": strike,
                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                **add_break_even(row),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "base_equity_ins_code"),
                        **add_details(row, BASE_EQUITY_BUY_COLUMN_MAPPING),
                    },
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "put_ins_code"),
                        **add_details(row, PUT_BUY_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"married_put, {len(result)} records." + Style.RESET_ALL)

    if result:
        list_key = "married_put"
        mongo_conn = MongodbInterface(db_name=mongo_db, collection_name=list_key)
        mongo_conn.insert_docs_into_collection(result)
