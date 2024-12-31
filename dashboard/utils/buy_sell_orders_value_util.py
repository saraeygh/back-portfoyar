from pytz import timezone

import pandas as pd
import jdatetime as jdt

from core.utils import RedisInterface, MongodbInterface
from core.configs import (
    STOCK_REDIS_DB,
    MARKET_WATCH_REDIS_KEY,
    DASHBOARD_MONGO_DB,
    BUY_SELL_ORDERS_COLLECTION,
)

from . import TSE_ORDER_BOOK

TEHRAN_TIMEZONE = timezone("Asia/Tehran")

redis_conn = RedisInterface(db=STOCK_REDIS_DB)
mongo_conn = MongodbInterface(
    db_name=DASHBOARD_MONGO_DB, collection_name=BUY_SELL_ORDERS_COLLECTION
)


BUY_SELL_ORDERS_COLUMNS = [
    "industrial_group",
    "paper_type",
    "buy_value",
    "sell_value",
]


def add_buy_value(row):
    order_book = pd.DataFrame(row.get("order_book"))
    order_book.rename(columns=TSE_ORDER_BOOK, inplace=True)
    order_book["buy_value"] = order_book["buy_volume"] * order_book["buy_price"]
    buy_value = order_book["buy_value"].sum()

    return buy_value


def add_sell_value(row):
    order_book = pd.DataFrame(row.get("order_book"))
    order_book.rename(columns=TSE_ORDER_BOOK, inplace=True)
    order_book["sell_value"] = order_book["sell_volume"] * order_book["sell_price"]
    sell_value = order_book["sell_value"].sum()

    return sell_value


def check_date():
    today_datetime = jdt.datetime.now(tz=TEHRAN_TIMEZONE)
    date = today_datetime.strftime("%Y-%m-%d")
    time = today_datetime.strftime("%H:%M")

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc and one_doc["date"] != date:
        mongo_conn.collection.delete_many({})

    return date, time


def buy_sell_orders_value():
    market_watch = pd.DataFrame(redis_conn.get_list_of_dicts(MARKET_WATCH_REDIS_KEY))
    market_watch["buy_value"] = market_watch.apply(add_buy_value, axis=1)
    market_watch["sell_value"] = market_watch.apply(add_sell_value, axis=1)
    market_watch = market_watch[BUY_SELL_ORDERS_COLUMNS]
    market_watch["industrial_group"] = market_watch["industrial_group"].astype(int)

    date, time = check_date()

    new_doc = {
        "date": date,
        "time": time,
        "order_book_value": market_watch.to_dict(orient="records"),
    }

    mongo_conn.collection.insert_one(new_doc)
