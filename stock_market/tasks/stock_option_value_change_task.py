import pandas as pd
import jdatetime as jdt
from core.utils import MongodbInterface, run_main_task, is_market_open_today

from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    RIAL_TO_MILLION_TOMAN,
    OPTION_MONGO_DB,
    OPTION_DATA_COLLECTION,
    AUTO_MODE,
    MANUAL_MODE,
)

from stock_market.utils import (
    CALL_OPTION,
    PUT_OPTION,
    FUND_PAPER,
    get_market_watch_data_from_mongo,
    is_in_schedule,
)


def get_instrument_info():
    mongo_conn = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name="instrument_info"
    )
    instrument_info = list(mongo_conn.collection.find({}, {"_id": 0}))

    instrument_info = pd.DataFrame(instrument_info)

    return instrument_info


def add_history(options: pd.DataFrame, history_collection_name: str):
    mongo_conn = MongodbInterface(
        db_name=STOCK_MONGO_DB, collection_name=history_collection_name
    )
    history = list(mongo_conn.collection.find({}, {"_id": 0}))

    history = pd.DataFrame(history)

    options = pd.merge(left=options, right=history, on="symbol")

    return options


def get_last_options(option_type):
    mongo_conn = MongodbInterface(
        db_name=OPTION_MONGO_DB, collection_name=OPTION_DATA_COLLECTION
    )
    last_options = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

    if option_type == CALL_OPTION:
        last_options = last_options[
            ["call_ins_code", "base_equity_symbol", "call_value", "call_close_price"]
        ]
        return last_options

    elif option_type == PUT_OPTION:
        last_options = last_options[
            ["put_ins_code", "base_equity_symbol", "put_value", "put_close_price"]
        ]

    else:
        return last_options

    return last_options


def get_asset_options_last_value_mean(options, option_type):
    value_col = "call_value"
    if option_type == PUT_OPTION:
        value_col = "put_value"

    base_equities = options["base_equity_symbol"].unique().tolist()
    options_list = list()
    for base_equity in base_equities:

        try:
            base_equity_options: pd.DataFrame = options[
                options["base_equity_symbol"] == base_equity
            ]
            last_mean = round(
                float(base_equity_options[value_col].mean()) / RIAL_TO_MILLION_TOMAN, 3
            )
        except Exception:
            last_mean = 0

        new_last_value_mean = {"symbol": base_equity, "last_mean": last_mean}
        options_list.append(new_last_value_mean)

    option_last_value_mean = pd.DataFrame(options_list)
    option_last_value_mean.dropna(inplace=True)

    return option_last_value_mean


def add_last_mean_to_history(row):
    chart = row.get("chart")
    history = chart.get("history")
    y = row.get("last_mean")
    x = str(jdt.date.today())
    history.append({"x": x, "y": y})
    chart["history"] = history

    return chart


def add_month_mean(row):
    try:
        history = pd.DataFrame(row.get("chart").get("history"))
        month_mean = float(history["y"].mean())
    except Exception:
        month_mean = 0

    return month_mean


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def add_pe(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    eps = row.get("eps")
    try:
        pe = close_mean / eps
    except Exception:
        pe = 0

    return pe


def add_ps(row):
    row = row.to_dict()
    close_mean = row.get("closing_price")
    psr = row.get("psr")
    try:
        ps = close_mean / psr
    except Exception:
        ps = 0

    return ps


def add_market_cap(row):
    row = row.to_dict()

    paper_type = row.get("paper_type")
    if paper_type == FUND_PAPER:
        market_cap = 0
        return market_cap

    close_mean = row.get("closing_price")
    total_share = row.get("total_share")
    try:
        market_cap = (close_mean * total_share) / RIAL_TO_BILLION_TOMAN
    except Exception:
        market_cap = 0

    return market_cap


def add_last_update(row):

    last_update = str(row.get("last_time"))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def stock_option_value_change_main(run_mode):
    if (
        is_in_schedule(9, 2, 0, 12, 40, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:
        instrument_info = get_instrument_info()
        instrument_info = instrument_info[
            [
                "ins_code",
                "symbol",
                "name",
                "sector_pe",
                "eps",
                "psr",
                "total_share",
                "month_mean_volume",
            ]
        ]
        option_types = [CALL_OPTION, PUT_OPTION]
        for option_type in option_types:
            options = get_last_options(option_type)
            if options.empty:
                return

            left_on = "call_ins_code"
            collection_name = "call_value_change"
            history_collection_name = "call_value_history"
            if option_type == PUT_OPTION:
                left_on = "put_ins_code"
                collection_name = "put_value_change"
                history_collection_name = "put_value_history"

            options = pd.merge(
                left=options,
                right=instrument_info,
                left_on=left_on,
                right_on="ins_code",
                how="left",
            )
            options.dropna(inplace=True)

            options = get_asset_options_last_value_mean(
                options=options, option_type=option_type
            )

            options = add_history(options, history_collection_name)
            options["chart"] = options.apply(add_last_mean_to_history, axis=1)
            options["month_mean"] = options.apply(add_month_mean, axis=1)
            options = options[options["month_mean"] != 0]
            options["value_change"] = options["last_mean"] / options["month_mean"]
            options = options[options["value_change"] != 0]

            options = pd.merge(
                left=options, right=instrument_info, on="symbol", how="left"
            )
            options = options[
                [
                    "ins_code",
                    "symbol",
                    "name",
                    "last_mean",
                    "month_mean",
                    "value_change",
                    "chart",
                    "total_share",
                    "sector_pe",
                    "psr",
                    "eps",
                ]
            ]

            last_data = get_market_watch_data_from_mongo()
            if last_data.empty:
                return
            last_data["daily_roi"] = (
                last_data["last_price_change"] / last_data["yesterday_price"]
            ) * 100
            last_data = last_data[
                [
                    "ins_code",
                    "closing_price",
                    "daily_roi",
                    "last_time",
                    "paper_type",
                    "last_price",
                ]
            ]
            options = pd.merge(left=options, right=last_data, on="ins_code", how="left")
            options["last_price_change"] = options["daily_roi"]

            options["link"] = options.apply(add_link, axis=1)
            options["pe"] = options.apply(add_pe, axis=1)
            options["ps"] = options.apply(add_ps, axis=1)
            options["market_cap"] = options.apply(add_market_cap, axis=1)
            options.dropna(inplace=True)
            options["last_time"] = options["last_time"].astype(int)
            options["last_update"] = options.apply(add_last_update, axis=1)
            options = options.to_dict(orient="records")

            if options:
                mongo_conn = MongodbInterface(
                    db_name=STOCK_MONGO_DB, collection_name=collection_name
                )
                mongo_conn.insert_docs_into_collection(documents=options)


def stock_option_value_change(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=stock_option_value_change_main,
        kw_args={"run_mode": run_mode},
    )
