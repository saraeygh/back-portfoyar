import pandas as pd
import numpy as np
import jdatetime
from tqdm import tqdm

from core.utils import MongodbInterface, run_main_task
from core.configs import (
    AUTO_MODE,
    MANUAL_MODE,
    TO_MILLION,
    RIAL_TO_BILLION_TOMAN,
    STOCK_MONGO_DB,
    NO_DAILY_HISTORY,
    NO_HISTORY_DATE,
)

from stock_market.utils import (
    MAIN_PAPER_TYPE_DICT,
    get_market_watch_data_from_redis,
    is_market_open,
)


def get_time(row):
    last_time = str(row.get("last_time"))
    if len(last_time) != 6:
        last_time = "0" + last_time
    last_time = f"{last_time[0:2]}:{last_time[2:4]}:{last_time[4:]}"

    return last_time


def calculate_buy_order_value(row):
    buy_orders = row.get("order_book", [])
    total_buy_value = 0
    for order_row in buy_orders:
        try:
            order_row_value = order_row["pmd"] * order_row["qmd"]
            total_buy_value += order_row_value
        except Exception:
            continue

    return total_buy_value


def calculate_sell_order_value(row):
    sell_orders = row.get("order_book", [])
    total_sell_value = 0
    for order_row in sell_orders:
        try:
            order_row_value = order_row["pmo"] * order_row["qmo"]
            total_sell_value += order_row_value
        except Exception:
            continue

    return total_sell_value


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def update_market_watch_data(market_watch: pd.DataFrame):
    market_watch = market_watch[
        market_watch["paper_type"].isin(list(MAIN_PAPER_TYPE_DICT.keys()))
    ]

    market_watch["last_time"] = market_watch.apply(get_time, axis=1)
    market_watch["last_date"] = str(jdatetime.date.today())

    market_watch["link"] = market_watch.apply(add_link, axis=1)

    market_watch["money_flow"] = (
        (market_watch["individual_buy_volume"] - market_watch["individual_sell_volume"])
        * market_watch["closing_price"]
    ) / RIAL_TO_BILLION_TOMAN

    market_watch["buy_pressure"] = (
        (
            (
                market_watch["individual_buy_volume"]
                / market_watch["individual_buy_count"]
            )
            * market_watch["closing_price"]
        )
    ) / (
        (market_watch["individual_sell_volume"] / market_watch["individual_sell_count"])
        * market_watch["closing_price"]
    )

    market_watch["buy_value"] = (
        (market_watch["individual_buy_volume"] * market_watch["closing_price"])
        / market_watch["individual_buy_count"]
    ) / RIAL_TO_BILLION_TOMAN

    market_watch["buy_order_value"] = market_watch.apply(
        calculate_buy_order_value, axis=1
    )

    market_watch["buy_ratio"] = market_watch["buy_order_value"] / (
        market_watch["volume"] * market_watch["closing_price"]
    )

    market_watch["sell_order_value"] = market_watch.apply(
        calculate_sell_order_value, axis=1
    )

    market_watch["sell_ratio"] = market_watch["sell_order_value"] / (
        market_watch["volume"] * market_watch["closing_price"]
    )

    market_watch["person_buy_volume"] = (
        market_watch["individual_buy_volume"] / TO_MILLION
    )
    market_watch["volume"] = market_watch["volume"] / TO_MILLION
    market_watch["base_volume"] = market_watch["base_volume"] / TO_MILLION
    market_watch["value"] = market_watch["value"] / RIAL_TO_BILLION_TOMAN
    market_watch["buy_order_value"] = (
        market_watch["buy_order_value"] / RIAL_TO_BILLION_TOMAN
    )
    market_watch["sell_order_value"] = (
        market_watch["sell_order_value"] / RIAL_TO_BILLION_TOMAN
    )
    market_watch["last_price_change"] = (
        market_watch["last_price_change"] / market_watch["yesterday_price"]
    ) * 100

    market_watch["closing_price_change"] = (
        market_watch["closing_price_change"] / market_watch["yesterday_price"]
    ) * 100

    return market_watch


def check_update_status(row):
    last_date = row.get("last_date")
    last_history_date = row.get("last_history_date")
    history = row.get("history")

    if last_date != last_history_date:
        return NO_DAILY_HISTORY
    return history


def get_history(row, index_name):
    new_time = row.get("last_time")
    index_value = round(row.get(index_name), 3)
    history = row.get("history")

    if history == NO_DAILY_HISTORY:
        history = list()
        history.append({"x": new_time, "y": index_value})
    else:
        time_set = set()
        for point in history:
            time_set.add(point["x"])

        if new_time not in time_set:
            history.append({"x": new_time, "y": index_value})

    return history


def update_market_watch_indices_main(run_mode):
    if run_mode == MANUAL_MODE or is_market_open():
        market_watch = update_market_watch_data(get_market_watch_data_from_redis())

        if market_watch.empty:
            return

        market_watch.drop_duplicates(subset=["symbol"], keep="last", inplace=True)

        common_columns = [
            "ins_code",
            "link",
            "symbol",
            "name",
            "last_time",
            "last_date",
            "trade_count",
            "volume",
            "value",
            "closing_price",
            "closing_price_change",
            "last_price",
            "last_price_change",
            "market_type",
            "paper_type",
            "buy_order_value",
            "sell_order_value",
        ]
        index_list = [
            "buy_pressure",
            "money_flow",
            "buy_value",
            "buy_ratio",
            "sell_ratio",
        ]
        for index_name in tqdm(index_list, desc="Update indices", ncols=10):
            index_columns = common_columns + [index_name]
            index_df = market_watch[index_columns]

            index_df.loc[:, :] = index_df.replace([np.inf, -np.inf], np.nan)
            index_df = index_df.dropna()

            mongo_conn = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name=index_name
            )
            history_df = list(mongo_conn.collection.find({}, {"_id": 0}))
            history_df = pd.DataFrame(history_df)
            if history_df.empty:
                index_df["history"] = NO_DAILY_HISTORY
                index_df["last_history_date"] = NO_HISTORY_DATE
            else:
                history_df = history_df[["ins_code", "history", "last_date"]]
                history_df = history_df.rename(
                    columns={"last_date": "last_history_date"}
                )
                index_df = index_df.merge(right=history_df, on="ins_code", how="left")

            index_df["history"] = index_df["history"].replace(np.nan, NO_DAILY_HISTORY)
            index_df["last_history_date"] = index_df["last_history_date"].replace(
                np.nan, NO_HISTORY_DATE
            )

            index_df["history"] = index_df.apply(check_update_status, axis=1)
            index_df["history"] = index_df.apply(
                get_history, axis=1, args=(index_name,)
            )
            index_df.drop("last_history_date", axis=1, inplace=True)
            index_df = index_df.to_dict(orient="records")

            mongo_conn.insert_docs_into_collection(documents=index_df)
            mongo_conn.client.close()


def update_market_watch_indices(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=update_market_watch_indices_main,
        kw_args={"run_mode": run_mode},
    )
