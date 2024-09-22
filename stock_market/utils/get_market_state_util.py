from core.utils import get_http_response
from . import TSETMC_REQUEST_HEADERS


def get_market_state(market_type_num):
    MARKET_OVERVIEW_URL = (
        f"https://cdn.tsetmc.com/api/MarketData/GetMarketOverview/{market_type_num}"
    )
    market_state = get_http_response(
        req_url=MARKET_OVERVIEW_URL, req_headers=TSETMC_REQUEST_HEADERS
    )
    try:
        market_state = market_state.json()
        market_state = market_state.get("marketOverview")
        market_state = market_state.get("marketState")
    except Exception:
        market_state = ""

    return market_state
