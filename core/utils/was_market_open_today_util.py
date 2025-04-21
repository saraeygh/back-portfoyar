from core.configs import (
    CORE_MONGO_DB,
    CORE_MARKET_STATE_COLLECTION,
    CORE_MARKET_STATE_KEY,
)
from core.utils import MongodbInterface


def is_market_open_today():
    mongo_conn = MongodbInterface(
        db_name=CORE_MONGO_DB, collection_name=CORE_MARKET_STATE_COLLECTION
    )
    market_state = mongo_conn.collection.find_one() or {}

    was_open = market_state.get(CORE_MARKET_STATE_KEY, False)

    return was_open
