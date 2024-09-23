from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import BASE_EQUITY_BUY_FEE, RIAL_TO_BILLION_TOMAN

from . import (
    CoveredCall,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=3)


def add_profits(row):
    profits = {
        "final_profit": 0,
        "monthly_profit": 0,
        "yearly_profit": 0,
    }

    strike_price = float(row.get("strike_price"))
    call_premium = float(row.get("call_best_buy_price"))
    base_equity_last_price = float(row.get("base_equity_last_price"))

    if base_equity_last_price != call_premium:
        profits["final_profit"] = (
            (strike_price / (base_equity_last_price - call_premium)) - 1
        ) * 100

    remained_day = row.get("remained_day")
    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits


def covered_call():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["call_best_buy_price"] > 0)
        & (distinct_end_date_options["call_last_update"] > 80000)
        & (distinct_end_date_options["base_equity_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(
        distinct_end_date_options, desc="covered_call", ncols=10
    ):
        for _, row in end_date_option.iterrows():
            strike = float(row.get("strike_price"))
            premium = float(row.get("call_best_buy_price"))
            asset_price = float(row.get("base_equity_last_price"))

            covered_call_strategy = CoveredCall(
                strike=strike, premium=premium, asset_price=asset_price
            )
            coordinates = covered_call_strategy.get_coordinate()

            profit_factor = premium - asset_price
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                # "base_equity_value": row.get("base_equity_value") / RIAL_TO_BILLION_TOMAN,
                "base_equity_last_price": asset_price,
                "base_equity_best_sell_price": row.get("base_equity_best_sell_price"),

                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": premium,
                "strike_price": strike,
                # "call_notional_value": row.get("call_notional_value") / RIAL_TO_BILLION_TOMAN,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,

                "remained_day": row.get("remained_day"),

                **add_profits(row),

                "profit_factor": profit_factor,

                "coordinates": coordinates,

                "actions": [
                    {
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("base_equity_ins_code")}",
                        "action": "خرید",
                        **add_action_detail(row, BASE_EQUITY_BUY_COLUMN_MAPPING),

                        "trade_fee": BASE_EQUITY_BUY_FEE * row.get("base_equity_best_sell_price"),
                        "liquidation_settlement_fee": 0,
                        "physical_settlement_fee": 0,
                        "total_fee": BASE_EQUITY_BUY_FEE * row.get("base_equity_best_sell_price"),
                    },
                    {
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("call_ins_code")}",
                        "action": "فروش",
                        **add_action_detail(row, CALL_SELL_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                ],
            }

            result.append(document)

    print(f"covered_call, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="covered_call", list_of_dicts=result)
