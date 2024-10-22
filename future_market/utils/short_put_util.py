from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN, FUTURE_REDIS_DB


from option_market.utils import (
    AddOption,
    Strategy,
    PUT_SELL_COLUMN_MAPPING,
    get_distinc_end_date_options,
    filter_rows_with_nan_values,
    add_action_detail,
)


redis_conn = RedisInterface(db=FUTURE_REDIS_DB)


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "put_value",
    *list(PUT_SELL_COLUMN_MAPPING.values()),
    #
    "base_equity_symbol",
    "base_equity_last_price",
]


def add_profits(remained_day, base_equity_last_price, strike_price):
    if base_equity_last_price != 0 and base_equity_last_price < strike_price:
        required_change = (
            (strike_price - base_equity_last_price) / base_equity_last_price
        ) * 100
    else:
        required_change = 0

    profits = {
        "final_profit": 100,
        "required_change": required_change,
        "remained_day": remained_day,
        "monthly_profit": "-",
        "yearly_profit": "-",
    }

    return profits


def short_put(option_data):
    distinct_end_date_options = option_data.loc[
        (option_data["put_best_buy_price"] > 0)
        & (option_data["put_last_update"] > 100000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="short_put", ncols=10):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            put_premium = float(row.get("put_best_buy_price"))

            add_option = AddOption()
            add_option.add_put_sell(strike=strike_price, premium=put_premium)
            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="short_put")
            coordinates = strategy.get_coordinate()

            remained_day = row.get("remained_day")
            profit_factor = put_premium
            base_equity_last_price = row.get("base_equity_last_price")
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "put_sell_symbol": row.get("put_symbol"),
                "put_best_buy_price": put_premium,
                "strike_price": strike_price,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                **add_profits(remained_day, base_equity_last_price, strike_price),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "فروش",
                        "link": "https://cdn.ime.co.ir/",
                        **add_action_detail(row, PUT_SELL_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(f"short_put, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="short_put", list_of_dicts=result)
