from uuid import uuid4
from tqdm import tqdm

from core.configs import RIAL_TO_BILLION_TOMAN
from core.utils import MongodbInterface, get_deviation_percent

from . import (
    Collar,
    CartesianProduct,
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
    "put_value",
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
    """Calculates strategy profitability considering transaction fees."""
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

    # Apply fee logic
    n_base_equity_price = add_base_equity_fee(base_equity_last_price, BUY)
    _, n_put_premium = add_option_fee(put_strike, put_best_sell_price, BUY, PUT)
    n_call_strike, n_call_premium = add_option_fee(
        call_strike, call_best_buy_price, SELL, CALL
    )

    # Net calculations
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
    """
    Scans for Collar strategies using Cartesian Product for pairing
    and the Collar class for coordinate generation.
    """
    # 1. Initial Data Cleaning
    valid_options = option_data.loc[
        (option_data["call_best_buy_price"] > 0)
        & (option_data["call_last_update"] > 90000)
        & (option_data["put_best_sell_price"] > 0)
        & (option_data["put_last_update"] > 90000)
        & (option_data["base_equity_last_price"] > 0)
    ].copy()

    # Get distinct groups (usually grouped by underlying and end_date)
    distinct_groups = get_distinc_end_date_options(valid_options)
    result = []

    for df_group in tqdm(distinct_groups, desc="Collar Scanner", ncols=100):
        # Filter mandatory columns
        df = filter_rows_with_nan_values(df_group, REQUIRED_COLUMNS)
        if df.empty:
            continue

        # 2. Generate Pairs using CartesianProduct
        # This replaces the nested loops. iterations=1 creates pairs.
        # strike_price_0 will be the 'Call' (higher) and strike_price_1 the 'Put' (lower)
        cp = CartesianProduct(df, iterations=1, include_equal=False)
        product_list = cp.get_cartesian_product()
        
        if not product_list:
            continue
            
        # The resulting dataframe contains all valid pairs
        pairs_df = product_list[-1]

        # 3. Process each pair
        for _, row in pairs_df.iterrows():
            # Identify roles based on the Cartesian logic (strike_price_0 > strike_price_1)
            call_strike = row["strike_price_0"]
            put_strike = row["strike_price_1"]
            
            # Since the row is a copied version of the original DF row, 
            # we need to ensure we grab the correct premium for the correct strike.
            # CartesianProduct copies the row of strike_price_0, so we use its prices.
            # We look up the 'Put' price from the original group for the strike_price_1.
            put_match = df[df["strike_price"] == put_strike].iloc[0]
            
            p_price = put_match["put_best_sell_price"]
            c_price = row["call_best_buy_price"]
            asset_price = row["base_equity_last_price"]

            # Instantiate Strategy Class for coordinates and specific logic
            collar_strategy = Collar(
                put_strike=put_strike,
                put_best_sell_price=p_price,
                call_strike=call_strike,
                call_best_buy_price=c_price,
                asset_price=asset_price,
            )

            # Build the document
            document = {
                "id": uuid4().hex,
                "base_equity_symbol": row["base_equity_symbol"],
                "base_equity_last_price": asset_price,
                "base_equity_best_sell_price": row["base_equity_best_sell_price"],
                "base_equity_order_book": row["base_equity_order_book"],
                "put_buy_symbol": put_match["put_symbol"],
                "put_best_sell_price": p_price,
                "put_buy_strike": put_strike,
                "put_value": put_match["put_value"] / RIAL_TO_BILLION_TOMAN,
                "call_sell_symbol": row["call_symbol"],
                "call_best_buy_price": c_price,
                "call_sell_strike": call_strike,
                "call_value": row["call_value"] / RIAL_TO_BILLION_TOMAN,
                "end_date": row["end_date"],
                "profit_factor": (c_price - asset_price - p_price),
                "strike_price_deviation": max(
                    (put_strike / asset_price - 1),
                    (call_strike / asset_price - 1),
                ),
                "coordinates": collar_strategy.get_coordinate(),
                **add_profits_with_fee(
                    row["remained_day"],
                    call_strike,
                    c_price,
                    put_strike,
                    p_price,
                    asset_price,
                ),
                "actions": [
                    {
                        "link": get_link_str(row, "base_equity_ins_code"),
                        "action": "خرید",
                        **add_details(row, BASE_EQUITY_BUY_COLUMN_MAPPING),
                    },
                    {
                        "link": get_link_str(put_match, "put_ins_code"),
                        "action": "خرید",
                        **add_details(put_match, PUT_BUY_COLUMN_MAPPING),
                    },
                    {
                        "link": get_link_str(row, "call_ins_code"),
                        "action": "فروش",
                        **add_details(row, CALL_SELL_COLUMN_MAPPING),
                    },
                ],
            }
            result.append(document)

    # 4. Save to Database
    print(f"Collar Scanner: {len(result)} records generated.")
    if result:
        mongo_conn = MongodbInterface(db_name=mongo_db, collection_name="collar")
        mongo_conn.insert_docs_into_collection(result)