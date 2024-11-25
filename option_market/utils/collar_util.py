from uuid import uuid4
from tqdm import tqdm
from core.configs import RIAL_TO_BILLION_TOMAN

from . import (
    AddOption,
    Strategy,
    CartesianProduct,
    CALL_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    get_distinc_end_date_options,
    add_action_detail,
    filter_rows_with_nan_values,
    get_link_str,
)

from colorama import Fore, Style


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


def collar(option_data, redis_conn):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_best_sell_price"] > 0)
        & (option_data["call_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="collar", ncols=10):
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
                base_equity_last_price = row.get("base_equity_last_price")
                document = {
                    "id": uuid4().hex,
                    "base_equity_symbol": row.get("base_equity_symbol"),
                    "base_equity_last_price": base_equity_last_price,
                    "call_sell_symbol_low": low_call_sell.get("call_symbol"),
                    "call_best_buy_price_low": low_premium,
                    "call_sell_strike_low": low_strike,
                    "call_sell_value_low": low_call_sell.get("call_value")
                    / RIAL_TO_BILLION_TOMAN,
                    "call_buy_symbol_high": high_call_buy.get("call_symbol"),
                    "call_best_sell_price_high": high_premium,
                    "call_buy_strike_high": high_strike,
                    "call_buy_value_low": high_call_buy.get("call_value")
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
                            "action": "فروش",
                            "link": get_link_str(low_call_sell, "call_ins_code"),
                            **add_action_detail(
                                low_call_sell, CALL_SELL_COLUMN_MAPPING
                            ),
                        },
                        {
                            "action": "خرید",
                            "link": get_link_str(high_call_buy, "call_ins_code"),
                            **add_action_detail(high_call_buy, CALL_BUY_COLUMN_MAPPING),
                        },
                        {
                            "action": "خرید",
                            "link": get_link_str(high_call_buy, "call_ins_code"),
                            **add_action_detail(high_call_buy, CALL_BUY_COLUMN_MAPPING),
                        },
                    ],
                }

                result.append(document)

    print(Fore.GREEN + f"collar, {len(result)} records." + Style.RESET_ALL)
    if result:
        redis_conn.bulk_push_list_of_dicts(list_key="collar", list_of_dicts=result)
