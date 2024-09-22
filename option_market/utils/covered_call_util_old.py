from core.utils import RedisInterface

from .get_options_util import get_options


def calc_break_even(row) -> float:
    premium = row["best_buy_price"]
    base_equit_price = row["base_equit_price"]
    break_even = base_equit_price - premium

    return break_even


def calc_final_profit_percent(row) -> float:
    premium = row["best_buy_price"]
    base_equit_price = row["base_equit_price"]
    strike = row["strike"]

    final_profit_percent = strike - base_equit_price + premium
    denominator = abs(premium - base_equit_price)

    if denominator == 0:
        return 0
    else:
        profit_percent = (final_profit_percent / denominator) * 100

    return round(profit_percent, 2)


def calc_monthly_final_profit_percent(row) -> float:
    final_profit_percent = row["final_profit_percent"]
    days_to_expire = row["days_to_expire"]

    if days_to_expire == 0:
        return 0
    else:
        monthly_profit_percent = (final_profit_percent / days_to_expire) * 30

    return round(monthly_profit_percent, 2)


def calc_annual_profit_percent(row) -> float:
    monthly_profit_percent = row["monthly_final_profit_percent"]
    annual_profit_percent = monthly_profit_percent * 12

    return round(annual_profit_percent, 2)


def covered_call_old() -> dict:

    covered_call_df = get_options(option_types=["calls"])

    covered_call_df = covered_call_df[covered_call_df["best_buy_price"] != 0]
    covered_call_df = covered_call_df.drop(["best_sell_price"], axis=1)

    covered_call_df["break_even"] = covered_call_df.apply(calc_break_even, axis=1)

    covered_call_df["final_profit_percent"] = covered_call_df.apply(
        calc_final_profit_percent, axis=1
    )

    covered_call_df["monthly_final_profit_percent"] = covered_call_df.apply(
        calc_monthly_final_profit_percent, axis=1
    )

    covered_call_df["annual_final_profit_percent"] = covered_call_df.apply(
        calc_annual_profit_percent, axis=1
    )
    options = covered_call_df.to_dict(orient="records")

    if options:
        redis_conn = RedisInterface(db=3)
        redis_conn.bulk_push_list_of_dicts(
            list_key="covered_calls", list_of_dicts=options
        )
        print(f"covered_calls, {len(options)} records.")
    else:
        print("Fetched no covered_calls data!")

    return options
