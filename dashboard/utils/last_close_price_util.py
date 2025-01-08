from pytz import timezone
import jdatetime as jdt

from core.utils import RedisInterface, MongodbInterface
from core.configs import STOCK_REDIS_DB, DASHBOARD_MONGO_DB, LAST_CLOSE_PRICE_COLLECTION

from stock_market.utils import get_market_watch_data_from_redis

TEHRAN_TIMEZONE = timezone("Asia/Tehran")

redis_conn = RedisInterface(db=STOCK_REDIS_DB)
mongo_conn = MongodbInterface(
    db_name=DASHBOARD_MONGO_DB, collection_name=LAST_CLOSE_PRICE_COLLECTION
)


LAST_CLOSE_PRICE_COLUMNS = [
    "industrial_group",
    "paper_type",
    "last_price_change",
    "close_price_change",
]


def add_last_price_change(row):
    try:
        last_price_change = (row.get("last_price_change") / row.get("last_price")) * 100
    except Exception:
        last_price_change = 0

    return last_price_change


def add_close_price_change(row):
    try:
        close_price_change = (
            row.get("closing_price_change") / row.get("closing_price")
        ) * 100
    except Exception:
        close_price_change = 0

    return close_price_change


def check_date():
    today_datetime = jdt.datetime.now(tz=TEHRAN_TIMEZONE)
    date = today_datetime.strftime("%Y-%m-%d")
    time = today_datetime.strftime("%H:%M")

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc and one_doc["date"] != date:
        mongo_conn.collection.delete_many({})

    return date, time


def last_close_price():
    market_watch = get_market_watch_data_from_redis()
    if not market_watch.empty:
        market_watch = market_watch[~market_watch["symbol"].str.contains(r"\d")]
        market_watch["last_price_change"] = market_watch.apply(
            add_last_price_change, axis=1
        )
        market_watch["close_price_change"] = market_watch.apply(
            add_close_price_change, axis=1
        )
        market_watch = market_watch[LAST_CLOSE_PRICE_COLUMNS]
        market_watch["industrial_group"] = market_watch["industrial_group"].astype(int)

        date, time = check_date()

        new_doc = {
            "date": date,
            "time": time,
            "last_close_price": market_watch.to_dict(orient="records"),
        }

        mongo_conn.collection.insert_one(new_doc)
