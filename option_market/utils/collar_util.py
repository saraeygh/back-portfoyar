from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    CALL_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)

redis_conn = RedisInterface(db=3)


def collar():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["call_best_buy_price"] > 0)
        & (distinct_end_date_options["call_best_sell_price"] > 0)
        & (distinct_end_date_options["call_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="collar", ncols=10):
        cartesians = CartesianProduct(dataframe=end_date_option)
        cartesians = cartesians.get_cartesian_product()
        if cartesians:
            for _, row in cartesians[0].iterrows():
                add_option = AddOption()

                low_strike = float(row.get("strike_price_1"))
                low_premium = end_date_option[
                    end_date_option["strike_price"] == low_strike
                ]
                low_premium = float(low_premium.get("call_best_buy_price").iloc[0])
                add_option.add_call_sell(strike=low_strike, premium=low_premium)

                high_strike = float(row.get("strike_price_0"))
                high_premium = end_date_option[
                    end_date_option["strike_price"] == high_strike
                ]
                high_premium = float(high_premium.get("call_best_sell_price").iloc[0])
                add_option.add_call_buy(strike=high_strike, premium=high_premium)
                add_option.add_call_buy(strike=high_strike, premium=high_premium)

                option_list = add_option.get_option_list
                strategy = Strategy(option_list=option_list, name="collar")

                coordinates = strategy.get_coordinate()

                low_call_sell = end_date_option.loc[
                    end_date_option["strike_price"] == low_strike
                ].iloc[0]

                high_call_buy = end_date_option.loc[
                    end_date_option["strike_price"] == high_strike
                ].iloc[0]

                profit_factor = low_premium + -2 * high_premium
                document = {
                    "id": uuid4().hex,

                    "base_equity_symbol": row.get("base_equity_symbol"),
                    # "base_equity_value": row.get("base_equity_value") / RIAL_TO_BILLION_TOMAN,
                    "base_equity_last_price": row.get("base_equity_last_price"),

                    "call_sell_symbol_low": low_call_sell.get("call_symbol"),
                    "call_best_buy_price_low": low_premium,
                    "call_sell_strike_low": low_strike,
                    # "call_sell_notional_value_low": low_call_sell.get("call_notional_value") / RIAL_TO_BILLION_TOMAN,
                    "call_sell_value_low": low_call_sell.get("call_value") / RIAL_TO_BILLION_TOMAN,

                    "call_buy_symbol_high": high_call_buy.get("call_symbol"),
                    "call_best_sell_price_high": high_premium,
                    "call_buy_strike_high": high_strike,
                    # "call_buy_notional_value_low": high_call_buy.get("call_notional_value") / RIAL_TO_BILLION_TOMAN,
                    "call_buy_value_low": high_call_buy.get("call_value") / RIAL_TO_BILLION_TOMAN,

                    "remained_day": row.get("remained_day"),

                    "end_date": row.get("end_date"),

                    "profit_factor": profit_factor,

                    "coordinates": coordinates,

                    "actions": [
                        {
                            "action": "فروش",
                            "link": f"https://www.tsetmc.com/instInfo/{low_call_sell.get("call_ins_code")}",
                            **add_action_detail(low_call_sell, CALL_SELL_COLUMN_MAPPING),
                            **add_option_fees(low_call_sell)
                        },
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{high_call_buy.get("call_ins_code")}",
                            **add_action_detail(high_call_buy, CALL_BUY_COLUMN_MAPPING),
                            **add_option_fees(high_call_buy)
                        },
                        {
                            "action": "خرید",
                            "link": f"https://www.tsetmc.com/instInfo/{high_call_buy.get("call_ins_code")}",
                            **add_action_detail(high_call_buy, CALL_BUY_COLUMN_MAPPING),
                            **add_option_fees(high_call_buy)
                        },
                    ],
                }

                result.append(document)

    print(f"collar, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="collar", list_of_dicts=result)
