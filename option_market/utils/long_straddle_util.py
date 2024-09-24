from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN
from . import (
    AddOption,
    Strategy,
    CALL_BUY_COLUMN_MAPPING, PUT_BUY_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=3)


def long_straddle():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["call_best_sell_price"] > 0)
        & (distinct_end_date_options["put_best_sell_price"] > 0)
        & (distinct_end_date_options["call_last_update"] > 80000)
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
        distinct_end_date_options, desc="long_straddle", ncols=10
    ):
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
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": row.get("base_equity_last_price"),

                "call_buy_symbol": row.get("call_symbol"),
                "call_best_sell_price": call_premium,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,

                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,

                "strike_price": strike_price,
                "remained_day": row.get("remained_day"),

                "profit_factor": profit_factor,

                "coordinates": coordinates,

                "actions": [
                    {
                        "action": "خرید",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("call_ins_code")}",
                        **add_action_detail(row, CALL_BUY_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                    {
                        "action": "خرید",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("put_ins_code")}",
                        **add_action_detail(row, PUT_BUY_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                ],
            }

            result.append(document)

    print(f"long_straddle, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="long_straddle", list_of_dicts=result)
