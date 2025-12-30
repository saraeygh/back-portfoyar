from uuid import uuid4
from tqdm import tqdm
import pandas as pd

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import MongodbInterface, get_deviation_percent

from . import (
    Collar,
    PUT_BUY_COLUMN_MAPPING,
    CALL_SELL_COLUMN_MAPPING,
    BASE_EQUITY_BUY_COLUMN_MAPPING,
    BUY,
    PUT,
    SELL,
    CALL,
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
    "call_value",
    *list(CALL_SELL_COLUMN_MAPPING.values()),
    "put_value",
    *list(PUT_BUY_COLUMN_MAPPING.values()),
    "base_equity_symbol",
    "base_equity_last_price",
]


def add_profits_with_fee(
    remained_day,
    call_strike,
    call_best_buy_price,
    put_strike,
    put_best_sell_price,
    base_equity_last_price,
):
    profits = {
        "final_profit": 0,
        "required_change": 0,
        "remained_day": remained_day,
        "monthly_profit": 0,
        "yearly_profit": 0,
        "fee": 0,
    }

    if base_equity_last_price < call_strike:
        profits["required_change"] = get_deviation_percent(
            call_strike, base_equity_last_price
        )

    n_base_equity_price = add_base_equity_fee(base_equity_last_price, BUY)
    _, n_put_premium = add_option_fee(put_strike, put_best_sell_price, BUY, PUT)
    n_call_strike, n_call_premium = add_option_fee(
        call_strike, call_best_buy_price, SELL, CALL
    )

    net_profit = (n_call_strike - n_base_equity_price) + (n_call_premium - n_put_premium)
    net_pay = abs(n_call_premium - (n_base_equity_price + n_put_premium))

    profits = get_profits(profits, net_profit, net_pay, remained_day)
    profits = get_fee_percent(
        profits,
        strike_sum=(put_strike + call_strike),
        premium_sum=(put_best_sell_price + call_best_buy_price),
        base_equity=[BUY, base_equity_last_price],
        net_pay=net_pay,
    )

    return profits


def collar(option_data, mongo_db: str):
    # Initial filtering for valid data
    valid_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["put_best_sell_price"] > 0)
        & (option_data["put_last_update"] > 90000)
        & (option_data["base_equity_last_update"] > 90000)
        & (option_data["base_equity_last_price"] > 0)
        & (option_data["base_equity_best_sell_price"] > 0)
    ].copy()

    # Group by end_date and get distinct maturity groups
    distinct_end_date_options = get_distinc_end_date_options(valid_options)

    result = []

    for end_date_df in tqdm(distinct_end_date_options, desc="collar", ncols=100):
        # Ensure required columns are present and drop rows with NaN in them
        df = filter_rows_with_nan_values(end_date_df, REQUIRED_COLUMNS)
        if df.empty:
            continue

        # Sort by strike_price ascending to ensure puts come before calls in combinations
        df = df.sort_values("strike_price").reset_index(drop=True)

        # Pre-extract repeated fields for performance
        strike_prices = df["strike_price"].values
        n_rows = len(df)

        # Use integer indexing for faster access
        for i in range(n_rows):
            put_row = df.iloc[i]

            put_strike = put_row.strike_price
            put_best_sell_price = put_row.put_best_sell_price
            base_equity_last_price = put_row.base_equity_last_price
            remained_day = put_row.remained_day

            # Only pair with rows where call strike > put strike (strict collar)
            for j in range(i + 1, n_rows):
                call_row = df.iloc[j]

                call_strike = call_row.strike_price
                call_best_buy_price = call_row.call_best_buy_price

                # Skip if strike not strictly increasing (core collar requirement)
                if call_strike <= put_strike:
                    continue

                collar_strategy = Collar(
                    put_strike=put_strike,
                    put_best_sell_price=put_best_sell_price,
                    call_strike=call_strike,
                    call_best_buy_price=call_best_buy_price,
                    asset_price=base_equity_last_price,
                )
                coordinates = collar_strategy.get_coordinate()

                profit_factor = (
                    call_best_buy_price - base_equity_last_price - put_best_sell_price
                )

                document = {
                    "id": uuid4().hex,
                    "base_equity_symbol": put_row.base_equity_symbol,
                    "base_equity_last_price": base_equity_last_price,
                    "base_equity_best_sell_price": put_row.base_equity_best_sell_price,
                    "base_equity_order_book": put_row.base_equity_order_book,
                    "put_buy_symbol": put_row.put_symbol,
                    "put_best_sell_price": put_best_sell_price,
                    "put_buy_strike": put_strike,
                    "put_value": put_row.put_value / RIAL_TO_BILLION_TOMAN,
                    "call_sell_symbol": call_row.call_symbol,
                    "call_best_buy_price": call_best_buy_price,
                    "call_sell_strike": call_strike,
                    "call_value": call_row.call_value / RIAL_TO_BILLION_TOMAN,
                    **add_profits_with_fee(
                        remained_day,
                        call_strike,
                        call_best_buy_price,
                        put_strike,
                        put_best_sell_price,
                        base_equity_last_price,
                    ),
                    "end_date": put_row.end_date,
                    "profit_factor": profit_factor,
                    "strike_price_deviation": max(
                        (put_strike / base_equity_last_price - 1),
                        (call_strike / base_equity_last_price - 1),
                    ),
                    "coordinates": coordinates,
                    "actions": [
                        {
                            "link": get_link_str(put_row, "base_equity_ins_code"),
                            "action": "خرید",
                            **add_details(put_row, BASE_EQUITY_BUY_COLUMN_MAPPING),
                        },
                        {
                            "link": get_link_str(put_row, "put_ins_code"),
                            "action": "خرید",
                            **add_details(put_row, PUT_BUY_COLUMN_MAPPING),
                        },
                        {
                            "link": get_link_str(call_row, "call_ins_code"),
                            "action": "فروش",
                            **add_details(call_row, CALL_SELL_COLUMN_MAPPING),
                        },
                    ],
                }

                result.append(document)

    print(f"collar, {len(result)} records generated.")
    if result:
        mongo_conn = MongodbInterface(db_name=mongo_db, collection_name="collar")
        mongo_conn.insert_docs_into_collection(result)