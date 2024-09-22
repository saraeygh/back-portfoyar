from core.utils import RedisInterface
from .get_options_util import get_options


def calc_break_even_percent(row) -> float:
    strike = row["strike"]
    premium = row["best_sell_price"]
    base_equit_price = row["base_equit_price"]

    if base_equit_price == 0:
        return 0

    break_even_percent = (((strike + premium) / base_equit_price) - 1) * 100

    return round(break_even_percent, 2)


def calc_break_even_monthly_percent(row) -> float:
    break_even_percent = row["break_even_percent"]
    days_to_expire = row["days_to_expire"]

    if days_to_expire == 0:
        return 0

    break_even_monthly_percent = (break_even_percent / days_to_expire) * 30

    return round(break_even_monthly_percent, 2)


def calc_leverage(row) -> float:
    base_equit_price = row["base_equit_price"]
    best_sell_price = row["best_sell_price"]

    if best_sell_price == 0:
        return 0

    leverage = base_equit_price / best_sell_price

    return round(leverage, 2)


def long_call_old() -> dict:
    long_calls_df = get_options(option_types=["calls"])

    long_calls_df = long_calls_df[long_calls_df["best_sell_price"] != 0]
    long_calls_df = long_calls_df.drop(["best_buy_price"], axis=1)

    long_calls_df["break_even_percent"] = long_calls_df.apply(
        calc_break_even_percent, axis=1
    )

    long_calls_df["break_even_monthly_percent"] = long_calls_df.apply(
        calc_break_even_monthly_percent, axis=1
    )

    long_calls_df = long_calls_df.rename(
        columns={"break_even_monthly_percent": "monthly_final_profit_percent"}
    )

    long_calls_df["leverage"] = long_calls_df.apply(calc_leverage, axis=1)

    options = long_calls_df.to_dict(orient="records")

    if options:
        redis_conn = RedisInterface(db=3)
        redis_conn.bulk_push_list_of_dicts(list_key="long_calls", list_of_dicts=options)
        print(f"long_calls, {len(options)} records.")
    else:
        print("Fetched no long_calls data!")

    return options
