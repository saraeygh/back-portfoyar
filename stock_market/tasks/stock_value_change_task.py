import pandas as pd
import jdatetime

from core.configs import (
    STOCK_MONGO_DB,
    RIAL_TO_BILLION_TOMAN,
    TO_MILLION,
    STOCK_REDIS_DB,
    AUTO_MODE,
)
from core.utils import (
    RedisInterface,
    MongodbInterface,
    print_task_info,
    send_task_fail_success_email,
)
from stock_market.utils import MAIN_PAPER_TYPE_DICT, get_market_watch_data_from_redis


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


redis_conn = RedisInterface(db=STOCK_REDIS_DB)


def stock_value_change_main():
    value_change = get_market_watch_data_from_redis()
    value_change = value_change[
        value_change["paper_type"].isin(list(MAIN_PAPER_TYPE_DICT.keys()))
    ]

    mongo_client = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="history")
    history = pd.DataFrame(list(mongo_client.collection.find({}, {"_id": 0})))
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
    value_change = value_change.to_dict(orient="records")

    mongo_client.collection = mongo_client.db["value_change"]
    mongo_client.insert_docs_into_collection(documents=value_change)


def stock_value_change(run_mode: str = AUTO_MODE):
    TASK_NAME = stock_value_change.__name__
    print_task_info(name=TASK_NAME)

    try:
        stock_value_change_main()
    except Exception as e:
        send_task_fail_success_email(task_name=TASK_NAME, exception=e)

    print_task_info(color="GREEN", name=TASK_NAME)
