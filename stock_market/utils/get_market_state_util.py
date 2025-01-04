from core.utils import MARKET_STATE, TSETMC_REQUEST_HEADERS, get_http_response
from core.models import FeatureToggle, ACTIVE

from . import MAIN_MARKET_TYPE_DICT


def get_market_state(market):
    MARKET_OVERVIEW_URL = (
        f"https://cdn.tsetmc.com/api/MarketData/GetMarketOverview/{market}"
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


def is_market_open():
    check_market = FeatureToggle.objects.get(name=MARKET_STATE["name"])
    if check_market.state != ACTIVE:
        return True

    for market, _ in MAIN_MARKET_TYPE_DICT.items():
        market_state = get_market_state(market)
        if market_state == check_market.value:
            return True

    return False
