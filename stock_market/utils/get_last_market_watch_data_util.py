import pandas as pd

from core.utils import (
    RedisInterface,
    TSETMC_REQUEST_HEADERS,
    get_http_response,
    replace_arabic_letters_pd,
)
from core.configs import STOCK_REDIS_DB, MARKET_WATCH_REDIS_KEY


def get_last_market_watch_data(
    market: int = 0, show_traded: str = "true", with_best_limit: str = "true"
):

    MARKET_WATCH_URL = (
        "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"
        f"?market={market}&industrialGroup="
        "&paperTypes[0]=1"
        "&paperTypes[1]=2"
        "&paperTypes[2]=3"
        "&paperTypes[3]=4"
        "&paperTypes[4]=5"
        "&paperTypes[5]=6"
        "&paperTypes[6]=7"
        "&paperTypes[7]=8"
        "&paperTypes[8]=9"
        f"&showTraded={show_traded}&withBestLimits={with_best_limit}"
    )
    last_data = get_http_response(
        req_url=MARKET_WATCH_URL, req_headers=TSETMC_REQUEST_HEADERS
    )
    try:
        last_data = last_data.json()
        last_data = last_data.get("marketwatch")
        last_data = pd.DataFrame(last_data)

    except Exception:
        return pd.DataFrame()

    last_data["lva"] = last_data.apply(replace_arabic_letters_pd, axis=1, args=("lva",))
    last_data["lvc"] = last_data.apply(replace_arabic_letters_pd, axis=1, args=("lvc",))

    return last_data


def get_market_watch_data_from_redis():
    redis_conn = RedisInterface(db=STOCK_REDIS_DB)
    market_watch = pd.DataFrame(
        redis_conn.get_list_of_dicts(list_key=MARKET_WATCH_REDIS_KEY)
    )

    return market_watch
