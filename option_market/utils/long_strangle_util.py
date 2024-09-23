from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    PUT_BUY_COLUMN_MAPPING,
    CALL_BUY_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)

redis_conn = RedisInterface(db=3)


def long_strangle():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["put_best_sell_price"] > 0)
        & (distinct_end_date_options["call_best_sell_price"] > 0)
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
        distinct_end_date_options, desc="long_strangle", ncols=10
    ):
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
                document = {
                    "id": uuid4().hex,

                    "base_equity_symbol": row.get("base_equity_symbol"),
                    # "base_equity_value": row.get("base_equity_value") / RIAL_TO_BILLION_TOMAN,
                    "base_equity_last_price": row.get("base_equity_last_price"),

                    "put_buy_symbol": put_buy_row.get("put_symbol"),
                    "put_buy_strike": low_strike,
                    # "put_buy_notional_value": put_buy_row.get("put_notional_value") / RIAL_TO_BILLION_TOMAN,
                    "put_buy_value": put_buy_row.get("put_value") / RIAL_TO_BILLION_TOMAN,

                    "call_buy_symbol": call_buy_row.get("call_symbol"),
                    "call_buy_strike": high_strike,
                    # "call_buy_notional_value": call_buy_row.get("call_notional_value") / RIAL_TO_BILLION_TOMAN,
                    "call_buy_value": call_buy_row.get("call_value") / RIAL_TO_BILLION_TOMAN,

                    "remained_day": row.get("remained_day"),

                    "profit_factor": profit_factor,

                    "coordinates": coordinates,

                    "actions": [
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{put_buy_row.get("put_ins_code")}",
                            **add_action_detail(put_buy_row, PUT_BUY_COLUMN_MAPPING),
                            **add_option_fees(put_buy_row)
                        },
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{call_buy_row.get("call_ins_code")}",
                            **add_action_detail(call_buy_row, CALL_BUY_COLUMN_MAPPING),
                            **add_option_fees(call_buy_row)
                        },
                    ],
                }

                result.append(document)

    print(f"long_strangle, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="long_strangle", list_of_dicts=result)
