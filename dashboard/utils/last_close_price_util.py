import jdatetime as jdt

from core.utils import MongodbInterface
from core.configs import DASHBOARD_MONGO_DB, LAST_CLOSE_PRICE_COLLECTION, TEHRAN_TZ

from stock_market.utils import get_market_watch_data_from_redis


LAST_CLOSE_PRICE_COLUMNS = [
    "industrial_group",
    "paper_type",
    "last_price_change",
    "closing_price_change",
]


def check_date():
    today_datetime = jdt.datetime.now(tz=TEHRAN_TZ)
    date = today_datetime.strftime("%Y/%m/%d")
    time = today_datetime.strftime("%H:%M")

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=LAST_CLOSE_PRICE_COLLECTION
    )

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc and one_doc["date"] != date:
        mongo_conn.collection.delete_many({})

    return date, time


def last_close_price():
    market_watch = get_market_watch_data_from_redis()
    if not market_watch.empty:
        market_watch = market_watch[~market_watch["symbol"].str.contains(r"\d")]
        market_watch["last_price_change"] = (
            market_watch["last_price_change"] / market_watch["last_price"]
        ) * 100

        market_watch["closing_price_change"] = (
            market_watch["closing_price_change"] / market_watch["closing_price"]
        ) * 100

        market_watch = market_watch[LAST_CLOSE_PRICE_COLUMNS]
        market_watch["industrial_group"] = market_watch["industrial_group"].astype(int)

        date, time = check_date()

        new_doc = {
            "date": date,
            "time": time,
            "last_close_price": market_watch.to_dict(orient="records"),
        }

        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=LAST_CLOSE_PRICE_COLLECTION
        )

        mongo_conn.collection.insert_one(new_doc)
