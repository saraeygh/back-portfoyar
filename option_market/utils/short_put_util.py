from uuid import uuid4
from tqdm import tqdm
from core.utils import RedisInterface
from core.configs import RIAL_TO_BILLION_TOMAN


from . import (
    AddOption,
    Strategy,
    PUT_SELL_COLUMN_MAPPING,
    get_options,
    get_distinc_end_date_options,
    convert_int_date_to_str_date,
    add_action_detail,
    add_option_fees,
)


redis_conn = RedisInterface(db=3)


def add_profits(remained_day):
    profits = {
        "final_profit": 100,
        "monthly_profit": 0,
        "yearly_profit": 0,
    }

    if remained_day != 0:
        profits["monthly_profit"] = (profits["final_profit"] / remained_day) * 30

    profits["yearly_profit"] = profits["monthly_profit"] * 12

    return profits



def short_put():
    distinct_end_date_options = get_options(option_types=["option_data"])
    distinct_end_date_options = distinct_end_date_options.loc[
        (distinct_end_date_options["put_best_buy_price"] > 0)
        & (distinct_end_date_options["put_last_update"] > 80000)
    ]
    distinct_end_date_options["end_date"] = distinct_end_date_options.apply(
        convert_int_date_to_str_date, args=("end_date",), axis=1
    )
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="short_put", ncols=10):
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
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                # "base_equity_value": row.get("base_equity_value") / RIAL_TO_BILLION_TOMAN,
                "base_equity_last_price": row.get("base_equity_last_price"),

                "put_sell_symbol": row.get("put_symbol"),
                "strike_price": strike_price,
                # "put_notional_value": row.get("put_notional_value") / RIAL_TO_BILLION_TOMAN,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                "remained_day": remained_day,

                **add_profits(remained_day),

                "profit_factor": profit_factor,

                "coordinates": coordinates,

                "actions": [
                    {
                        "action": "فروش",
                        "link": f"https://www.tsetmc.com/instInfo/{row.get("put_ins_code")}",
                        **add_action_detail(row, PUT_SELL_COLUMN_MAPPING),
                        **add_option_fees(row)
                    },
                ],
            }

            result.append(document)

    print(f"short_put, {len(result)} records.")

    redis_conn.bulk_push_list_of_dicts(list_key="short_put", list_of_dicts=result)
