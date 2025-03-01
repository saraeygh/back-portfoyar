from uuid import uuid4
from tqdm import tqdm
from core.configs import RIAL_TO_BILLION_TOMAN, FUTURE_REDIS_DB, FUTURE_MONGO_DB
from core.utils import RedisInterface, MongodbInterface

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    PUT_BUY_COLUMN_MAPPING,
    CALL_BUY_COLUMN_MAPPING,
    get_distinc_end_date_options,
    add_details,
    filter_rows_with_nan_values,
    get_link_str,
)

from colorama import Fore, Style


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "put_value",
    "call_value",
    *list(PUT_BUY_COLUMN_MAPPING.values()),
    *list(CALL_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def long_strangle(option_data, redis_db_num: int):
    distinct_end_date_options = option_data.loc[
        (option_data["put_best_sell_price"] > 0)
        & (option_data["call_best_sell_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["put_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="long_strangle", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue

        cartesians = CartesianProduct(dataframe=end_date_option)
        cartesians = cartesians.get_cartesian_product()

        if cartesians:
            for _, row in cartesians[0].iterrows():
                add_option = AddOption()

                low_strike = float(row.get("strike_price_1"))
                low_premium = end_date_option[
                    end_date_option["strike_price"] == low_strike
                ]
                low_premium = float(low_premium.get("put_best_sell_price").iloc[0])
                add_option.add_put_buy(strike=low_strike, premium=low_premium)

                high_strike = float(row.get("strike_price_0"))
                high_premium = end_date_option[
                    end_date_option["strike_price"] == high_strike
                ]
                high_premium = float(high_premium.get("call_best_sell_price").iloc[0])
                add_option.add_call_buy(strike=high_strike, premium=high_premium)

                option_list = add_option.get_option_list
                strategy = Strategy(option_list=option_list, name="long_strangle")

                coordinates = strategy.get_coordinate()

                put_buy_row = end_date_option.loc[
                    end_date_option["strike_price"] == low_strike
                ].iloc[0]

                call_buy_row = end_date_option.loc[
                    end_date_option["strike_price"] == high_strike
                ].iloc[0]

                profit_factor = -1 * (low_premium + high_premium)
                base_equity_last_price = row.get("base_equity_last_price")
                document = {
                    "id": uuid4().hex,
                    "base_equity_symbol": row.get("base_equity_symbol"),
                    "base_equity_last_price": base_equity_last_price,
                    "base_equity_order_book": row.get("base_equity_order_book"),
                    "put_buy_symbol": put_buy_row.get("put_symbol"),
                    "put_best_sell_price": low_premium,
                    "put_buy_strike": low_strike,
                    "put_buy_value": put_buy_row.get("put_value")
                    / RIAL_TO_BILLION_TOMAN,
                    "call_buy_symbol": call_buy_row.get("call_symbol"),
                    "call_best_sell_price": high_premium,
                    "call_buy_strike": high_strike,
                    "call_buy_value": call_buy_row.get("call_value")
                    / RIAL_TO_BILLION_TOMAN,
                    "remained_day": row.get("remained_day"),
                    "end_date": row.get("end_date"),
                    "profit_factor": profit_factor,
                    "strike_price_deviation": max(
                        ((low_strike / base_equity_last_price) - 1),
                        ((high_strike / base_equity_last_price) - 1),
                    ),
                    "coordinates": coordinates,
                    "actions": [
                        {
                            "action": "خرید",
                            "link": get_link_str(put_buy_row, "put_ins_code"),
                            **add_details(put_buy_row, PUT_BUY_COLUMN_MAPPING),
                        },
                        {
                            "action": "خرید",
                            "link": get_link_str(call_buy_row, "call_ins_code"),
                            **add_details(call_buy_row, CALL_BUY_COLUMN_MAPPING),
                        },
                    ],
                }

                result.append(document)

    print(Fore.GREEN + f"long_strangle, {len(result)} records." + Style.RESET_ALL)
    if result:
        list_key = "long_strangle"
        if redis_db_num == FUTURE_REDIS_DB:
            mongo_conn = MongodbInterface(db_name=FUTURE_MONGO_DB)
            mongo_conn.collection = mongo_conn.db[list_key]
            mongo_conn.insert_docs_into_collection(result)
        else:
            redis_conn = RedisInterface(db=redis_db_num)
            redis_conn.bulk_push_list_of_dicts(list_key=list_key, list_of_dicts=result)
