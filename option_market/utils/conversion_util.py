from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import BASE_EQUITY_BUY_FEE, RIAL_TO_BILLION_TOMAN

from . import (
    Conversion,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    PUT_BUY_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=3)


def add_profits(row, net_profit, profit_factor):
    remained_day = row.get("remained_day")

    profits = {
        "final_profit": (net_profit / profit_factor) * 100,
        "required_change": 0,
        "remained_day": remained_day,
        "monthly_profit": "-",
        "yearly_profit": "-",
    }

    return profits


def conversion():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["call_best_buy_price"] > 0)
        & (distinct_end_date_options["put_best_sell_price"] > 0)
        & (distinct_end_date_options["call_last_update"] > 80000)
        & (distinct_end_date_options["put_last_update"] > 80000)
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
        distinct_end_date_options, desc="conversion", ncols=10
    ):
        for _, row in end_date_option.iterrows():
            strike = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_buy_price"))
            put_premium = float(row.get("put_best_sell_price"))
            asset_price = float(row.get("base_equity_last_price"))

            covered_call_strategy = Conversion(
                strike=strike, call_premium=call_premium, put_premium=put_premium, asset_price=asset_price
            )
            coordinates = covered_call_strategy.get_coordinate()

            profit_factor = call_premium - put_premium - asset_price
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": asset_price,
                "base_equity_best_sell_price": row.get("base_equity_best_sell_price"),

                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": call_premium,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,

                "strike_price": strike,

                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,

                **add_profits(row, covered_call_strategy.net_profit, abs(profit_factor)),

                "end_date": row.get("end_date"),

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
                    {
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("put_ins_code")}",
                        "action": "خرید",
                        **add_action_detail(row, PUT_BUY_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                ],
            }

            result.append(document)

    print(f"Conversion, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="conversion", list_of_dicts=result)
