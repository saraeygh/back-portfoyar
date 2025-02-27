from pytz import timezone

import jdatetime as jdt

from core.utils import MongodbInterface
from core.configs import (
    DASHBOARD_MONGO_DB,
    OPTION_VALUE_ANALYSIS_COLLECTION,
    RIAL_TO_BILLION_TOMAN,
)

from option_market.utils import get_option_data_from_redis
from stock_market.utils import (
    STOCK_PAPER,
    INITIAL_MARKET_PAPER,
    PRIORITY_PAPER,
    FUND_PAPER,
    get_market_watch_data_from_redis,
)


TEHRAN_TIMEZONE = timezone("Asia/Tehran")


def check_date():
    today_datetime = jdt.datetime.now(tz=TEHRAN_TIMEZONE)
    date = today_datetime.strftime("%Y/%m/%d")
    time = today_datetime.strftime("%H:%M")

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
    )

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc and one_doc["date"] != date:
        mongo_conn.collection.delete_many({})

    return date, time


def option_value_analysis():
    market_watch = get_market_watch_data_from_redis()

    market_value = market_watch[
        market_watch["paper_type"].isin(
            [STOCK_PAPER, INITIAL_MARKET_PAPER, PRIORITY_PAPER, FUND_PAPER]
        )
    ]["value"].sum()

    option_data = get_option_data_from_redis()

    date, time = check_date()

    call_value = option_data["call_value"].sum()
    put_value = option_data["put_value"].sum()
    option_value = call_value + put_value
    call_to_put = call_value / put_value

    new_doc = {
        "date": date,
        "time": time,
        "call_value": int(call_value / RIAL_TO_BILLION_TOMAN),
        "put_value": int(put_value / RIAL_TO_BILLION_TOMAN),
        "option_value": int(option_value / RIAL_TO_BILLION_TOMAN),
        "call_to_put": round(call_to_put, 3),
        "option_to_market": round(option_value / market_value, 3),
    }

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
    )

    mongo_conn.collection.insert_one(new_doc)
