from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN, OPTION_REDIS_DB

from . import (
    AddOption,
    Strategy,
    PUT_BUY_COLUMN_MAPPING,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=OPTION_REDIS_DB)


def long_put(option_data):
    distinct_end_date_options = option_data.loc[
        (option_data["put_best_sell_price"] > 0)
        & (option_data["put_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="long_put", ncols=10):
        for _, row in end_date_option.iterrows():
            strike_price = float(row.get("strike_price"))
            put_premium = float(row.get("put_best_sell_price"))

            add_option = AddOption()
            add_option.add_put_buy(strike=strike_price, premium=put_premium)
            option_list = add_option.get_option_list
            strategy = Strategy(option_list=option_list, name="long_put")
            coordinates = strategy.get_coordinate()

            profit_factor = -1 * put_premium
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": row.get("base_equity_last_price"),
                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "strike_price": strike_price,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                "remained_day": row.get("remained_day"),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("put_ins_code")}",
                        **add_action_detail(row, PUT_BUY_COLUMN_MAPPING),
                        **add_option_fees(row),
                    },
                ],
            }

            result.append(document)

    print(f"long_put, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="long_put", list_of_dicts=result)
