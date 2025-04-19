from core.configs import (
    CORE_MONGO_DB,
    CORE_MARKET_STATE_COLLECTION,
    CORE_MARKET_STATE_KEY,
)
from core.utils import MongodbInterface, run_main_task

from stock_market.utils import is_market_open


def is_market_open_today_main():
    mongo_conn = MongodbInterface(
        db_name=CORE_MONGO_DB, collection_name=CORE_MARKET_STATE_COLLECTION
    )
    if is_market_open():
        market_state = True
    else:
        market_state = False

    mongo_conn.collection.delete_many({})
    mongo_conn.collection.insert_one(
        {
            CORE_MARKET_STATE_KEY: market_state,
        }
    )


def is_market_open_today():
    run_main_task(
        main_task=is_market_open_today_main,
        daily=True,
    )
