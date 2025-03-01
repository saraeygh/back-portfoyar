from uuid import uuid4
from tqdm import tqdm
from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN, FUTURE_REDIS_DB, FUTURE_MONGO_DB
from core.utils import RedisInterface, MongodbInterface

from . import (
    AddOption,
    Strategy,
    CALL_BUY_COLUMN_MAPPING,
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
    "call_value",
    *list(CALL_BUY_COLUMN_MAPPING.values()),
    "put_value",
    *list(PUT_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def long_straddle(option_data, redis_db_num: int):
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
            base_equity_last_price = row.get("base_equity_last_price")
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "call_buy_symbol": row.get("call_symbol"),
                "call_best_sell_price": call_premium,
                "base_equity_order_book": row.get("base_equity_order_book"),
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                "strike_price": strike_price,
                "remained_day": row.get("remained_day"),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike_price / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "call_ins_code"),
                        **add_details(row, CALL_BUY_COLUMN_MAPPING),
                    },
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "put_ins_code"),
                        **add_details(row, PUT_BUY_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"long_straddle, {len(result)} records." + Style.RESET_ALL)
    if result:
        list_key = "long_straddle"
        if redis_db_num == FUTURE_REDIS_DB:
            mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
            mongo_conn.collection = mongo_conn.db[list_key]
            mongo_conn.insert_docs_into_collection(result)
        else:
            redis_conn = RedisInterface(db=redis_db_num)
            redis_conn.bulk_push_list_of_dicts(list_key=list_key, list_of_dicts=result)
