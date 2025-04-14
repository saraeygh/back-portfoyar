import pandas as pd
import jdatetime

from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    TO_MILLION,
    AUTO_MODE,
    MANUAL_MODE,
)
from core.utils import MongodbInterface, run_main_task
from stock_market.utils import (
    MAIN_PAPER_TYPE_DICT,
    get_market_watch_data_from_mongo,
    is_in_schedule,
    remove_fixed_income_mixed,
)


def add_last_update(row):
    last_update = str(row.get("last_time"))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def add_today_to_history(row, last_date):
    history = list(row.get("history"))
    value = int(row.get("value"))
    history.append({"x": last_date, "y": value})

    return history


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def stock_value_change_main(run_mode):
    if run_mode == MANUAL_MODE or is_in_schedule(8, 55, 0, 12, 40, 0):
        value_change = get_market_watch_data_from_mongo()
        value_change = value_change[
            value_change["paper_type"].isin(list(MAIN_PAPER_TYPE_DICT.keys()))
        ]

        mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="history")
        history = pd.DataFrame(list(mongo_conn.collection.find({}, {"_id": 0})))
        if history.empty:
            return

        value_change = value_change.merge(right=history, on="ins_code", how="left")
        del history

        value_change["last_price_change"] = (
            value_change["last_price_change"] / value_change["yesterday_price"]
        ) * 100
        value_change["closing_price_change"] = (
            value_change["closing_price_change"] / value_change["yesterday_price"]
        ) * 100
        value_change["value_change"] = value_change["value"] / value_change["mean"]

        value_change["last_update"] = value_change.apply(add_last_update, axis=1)
        value_change.dropna(inplace=True)

        if value_change.empty:
            return

        value_change["value"] = value_change["value"] / RIAL_TO_BILLION_TOMAN
        value_change["mean"] = value_change["mean"] / RIAL_TO_BILLION_TOMAN
        value_change["volume"] = value_change["volume"] / TO_MILLION
        value_change["link"] = value_change.apply(add_link, axis=1)

        last_date = str(jdatetime.date.today())
        value_change["history"] = value_change.apply(
            add_today_to_history, axis=1, args=(last_date,)
        )

        if value_change.empty:
            return

        value_change.drop_duplicates(subset=["symbol"], keep="last", inplace=True)
        value_change = remove_fixed_income_mixed(value_change)
        value_change = value_change.to_dict(orient="records")

        mongo_conn.collection = mongo_conn.db["value_change"]
        mongo_conn.insert_docs_into_collection(documents=value_change)


def stock_value_change(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=stock_value_change_main,
        kw_args={"run_mode": run_mode},
    )
