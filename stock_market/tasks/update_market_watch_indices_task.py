import pandas as pd
import jdatetime as jdt
from tqdm import tqdm

from core.utils import MongodbInterface, run_main_task
from core.configs import (
    AUTO_MODE,
    MANUAL_MODE,
    TO_MILLION,
    RIAL_TO_BILLION_TOMAN,
    STOCK_MONGO_DB,
    TEHRAN_TZ,
)


from stock_market.utils import (
    MAIN_PAPER_TYPE_DICT,
    get_market_watch_data_from_mongo,
    is_in_schedule,
    remove_fixed_income_mixed,
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
        (market_watch["paper_type"].isin(list(MAIN_PAPER_TYPE_DICT.keys())))
        & (market_watch["individual_buy_count"] != 0)
        & (market_watch["individual_sell_count"] != 0)
        & (market_watch["volume"] != 0)
        & (market_watch["closing_price"] != 0)
        & (market_watch["yesterday_price"] != 0)
    ]
    market_watch = market_watch.copy()
    market_watch["last_time"] = market_watch.apply(get_time, axis=1)
    market_watch["last_date"] = str(jdt.date.today())

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

    market_watch = remove_fixed_income_mixed(market_watch)

    return market_watch


def check_date(mongo_conn):

    today_datetime = jdt.datetime.now(tz=TEHRAN_TZ)
    today_date = today_datetime.strftime("%Y-%m-%d")

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc and one_doc["last_date"] != today_date:
        mongo_conn.collection.delete_many({})

    return today_date


def add_first_history(row, index_name):
    first_history = [
        {
            "x": row.get("last_time"),
            "y": round(row.get(index_name), 3),
        }
    ]

    return first_history


def get_history(row, index_name):
    new_history = {
        "x": row.get("last_time"),
        "y": round(row.get(index_name), 3),
    }
    history = row.get("history")
    history.append(new_history)

    return history


def update_market_watch_indices_main(run_mode):
    if run_mode == MANUAL_MODE or is_in_schedule(9, 0, 0, 18, 0, 0):
        mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB)

        market_watch = get_market_watch_data_from_mongo()
        if market_watch.empty:
            return
        market_watch = update_market_watch_data(market_watch)

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
            mongo_conn.collection = mongo_conn.db[index_name]
            today_date = check_date(mongo_conn)

            index_columns = common_columns + [index_name]
            index_df = market_watch[index_columns]

            history_df = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))
            if not history_df.empty:
                history_df = history_df[["ins_code", "history", "last_date"]]
                history_df = history_df.rename(
                    columns={"last_date": "last_history_date"}
                )
                index_df = index_df.merge(right=history_df, on="ins_code", how="left")
                index_df.dropna(inplace=True)
                index_df["history"] = index_df.apply(
                    get_history, axis=1, args=(index_name,)
                )
            else:
                index_df["history"] = index_df.apply(
                    add_first_history, args=(index_name,), axis=1
                )
                index_df["last_history_date"] = today_date

            index_df.drop("last_history_date", axis=1, inplace=True)
            index_df = index_df.to_dict(orient="records")

            mongo_conn.insert_docs_into_collection(documents=index_df)


def update_market_watch_indices(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=update_market_watch_indices_main,
        kw_args={"run_mode": run_mode},
    )
