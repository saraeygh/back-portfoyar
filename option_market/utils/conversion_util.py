from uuid import uuid4
from tqdm import tqdm

from colorama import Fore, Style

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import MongodbInterface

from . import (
    Conversion,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    PUT_BUY_COLUMN_MAPPING,
    CALL,
    SELL,
    PUT,
    BUY,
    get_distinc_end_date_options,
    add_details,
    filter_rows_with_nan_values,
    get_link_str,
    add_option_fee,
    add_base_equity_fee,
    get_profits,
    get_fee_percent,
)


REQUIRED_COLUMNS = [
    "strike_price",
    "end_date",
    "remained_day",
    #
    "call_value",
    "put_value",
    *list(CALL_SELL_COLUMN_MAPPING.values()),
    *list(PUT_BUY_COLUMN_MAPPING.values()),
    #
    "base_equity_last_price",
    *list(BASE_EQUITY_BUY_COLUMN_MAPPING.values()),
]


def add_profits_with_fee(
    remained_day, strike, call_premium, put_premium, base_equity_price
):
    profits = {
        "final_profit": 0,
        "required_change": 0,
        "remained_day": remained_day,
        "monthly_profit": 0,
        "yearly_profit": 0,
        "fee": 0,
    }

    n_strike, n_call_premium = add_option_fee(strike, call_premium, SELL, CALL)
    n_strike, n_put_premium = add_option_fee(strike, put_premium, BUY, PUT)
    n_base_equity_price = add_base_equity_fee(base_equity_price, BUY)

    net_in = n_call_premium - n_put_premium - n_base_equity_price + n_strike
    net_out = abs(n_call_premium - n_put_premium - n_base_equity_price)
    profits = get_profits(profits, net_in, net_out, remained_day)

    profits = get_fee_percent(
        profits,
        strike_sum=strike,
        premium_sum=sum([call_premium, put_premium]),
        base_equity=[BUY, base_equity_price],
        net_pay=net_out,
    )

    return profits


def conversion(option_data, mongo_db: str):
    distinct_end_date_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["put_best_sell_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["put_last_update"] > 90000)
        & (option_data["base_equity_last_update"] > 90000)
    ]
    distinct_end_date_options = get_distinc_end_date_options(
        option_data=distinct_end_date_options
    )

    result = []
    for end_date_option in tqdm(distinct_end_date_options, desc="conversion", ncols=10):
        end_date_option = filter_rows_with_nan_values(end_date_option, REQUIRED_COLUMNS)
        if end_date_option.empty:
            continue

        for _, row in end_date_option.iterrows():
            strike = float(row.get("strike_price"))
            call_premium = float(row.get("call_best_buy_price"))
            put_premium = float(row.get("put_best_sell_price"))
            base_equity_last_price = float(row.get("base_equity_last_price"))

            conversion_strategy = Conversion(
                strike=strike,
                call_premium=call_premium,
                put_premium=put_premium,
                asset_price=base_equity_last_price,
            )
            coordinates = conversion_strategy.get_coordinate()

            profit_factor = call_premium - put_premium - base_equity_last_price
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row.get("base_equity_symbol"),
                "base_equity_last_price": base_equity_last_price,
                "base_equity_best_sell_price": row.get("base_equity_best_sell_price"),
                "base_equity_order_book": row.get("base_equity_order_book"),
                "call_sell_symbol": row.get("call_symbol"),
                "call_best_buy_price": call_premium,
                "call_value": row.get("call_value") / RIAL_TO_BILLION_TOMAN,
                "strike_price": strike,
                "put_buy_symbol": row.get("put_symbol"),
                "put_best_sell_price": put_premium,
                "put_value": row.get("put_value") / RIAL_TO_BILLION_TOMAN,
                **add_profits_with_fee(
                    row.get("remained_day"),
                    strike,
                    call_premium,
                    put_premium,
                    base_equity_last_price,
                ),
                "end_date": row.get("end_date"),
                "profit_factor": profit_factor,
                "strike_price_deviation": ((strike / base_equity_last_price) - 1),
                "coordinates": coordinates,
                "actions": [
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "base_equity_ins_code"),
                        **add_details(row, BASE_EQUITY_BUY_COLUMN_MAPPING),
                    },
                    {
                        "action": "فروش",
                        "link": get_link_str(row, "call_ins_code"),
                        **add_details(row, CALL_SELL_COLUMN_MAPPING),
                    },
                    {
                        "action": "خرید",
                        "link": get_link_str(row, "put_ins_code"),
                        **add_details(row, PUT_BUY_COLUMN_MAPPING),
                    },
                ],
            }

            result.append(document)

    print(Fore.GREEN + f"conversion, {len(result)} records." + Style.RESET_ALL)

    if result:
        list_key = "conversion"
        mongo_conn = MongodbInterface(db_name=mongo_db, collection_name=list_key)
        mongo_conn.insert_docs_into_collection(result)
