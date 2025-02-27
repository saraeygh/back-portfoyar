from uuid import uuid4
from tqdm import tqdm
from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import RedisInterface, get_deviation_percent

from . import (
    CoveredCall,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    BUY,
    SELL,
    CALL,
    get_distinc_end_date_options,
    add_details,
    filter_rows_with_nan_values,
    get_link_str,
    get_profits,
    get_fee_percent,
    add_option_fee,
    add_base_equity_fee,
)


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "call_value",
    *list(CALL_SELL_COLUMN_MAPPING.values()),
    #
    "base_equity_last_price",
    *list(BASE_EQUITY_BUY_COLUMN_MAPPING.values()),
]


def add_profits_with_fee(remained_day, strike, premium, base_equity_price):
    profits = {
        "final_profit": 0,
        "required_change": 0,
        "remained_day": remained_day,
        "monthly_profit": 0,
        "yearly_profit": 0,
        "fee": 0,
    }

    if base_equity_price != 0 and base_equity_price < strike:
        profits["required_change"] = get_deviation_percent(strike, base_equity_price)

    n_strike, n_premium = add_option_fee(strike, premium, SELL, CALL)
    n_base_equity_price = add_base_equity_fee(base_equity_price, BUY)

    net_in = n_strike - (n_base_equity_price - n_premium)
    net_out = n_base_equity_price - n_premium
    profits = get_profits(profits, net_in, net_out, remained_day)

    profits = get_fee_percent(
        profits,
        strike_sum=strike,
        premium_sum=premium,
        base_equity=[BUY, base_equity_price],
        net_pay=net_out,
    )

    return profits


def covered_call(option_data, redis_db_num: int):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["base_equity_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="covered_call", ncols=10
    ):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue
        for _, row in end_date_option.iterrows():
            strike = float(row.get("strike_price"))
            premium = float(row.get("call_best_buy_price"))
            base_equity_last_price = float(row.get("base_equity_last_price"))

            covered_call_strategy = CoveredCall(
                strike=strike, premium=premium, asset_price=base_equity_last_price
            )
            coordinates = covered_call_strategy.get_coordinate()

            profit_factor = premium - base_equity_last_price
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_best_sell_price": row.get("base_equity_best_sell_price"),
                "base_equity_order_book": row.get("base_equity_order_book"),
                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": premium,
                "strike_price": strike,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                **add_profits_with_fee(
                    row.get("remained_day"),
                    strike,
                    premium,
                    base_equity_last_price,
                ),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "link": get_link_str(row, "base_equity_ins_code"),
                        "action": "خرید",
                        **add_details(row, BASE_EQUITY_BUY_COLUMN_MAPPING),
                    },
                    {
                        "link": get_link_str(row, "call_ins_code"),
                        "action": "فروش",
                        **add_details(row, CALL_SELL_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"covered_call, {len(result)} records." + Style.RESET_ALL)

    if result:
        redis_conn = RedisInterface(db=redis_db_num)
        redis_conn.bulk_push_list_of_dicts(
            list_key="covered_call", list_of_dicts=result
        )
