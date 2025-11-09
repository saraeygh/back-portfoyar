import jdatetime as jdt

from core.utils import MARKET_STATE, TSETMC_REQUEST_HEADERS, get_http_response
from core.configs import TEHRAN_TZ
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


def is_in_schedule(
    s_hour: int = 0,
    s_minute: int = 0,
    s_second: int = 0,
    e_hour: int = 0,
    e_minute: int = 0,
    e_second: int = 0,
):
    now = jdt.datetime.now(tz=TEHRAN_TZ)

    start = now.replace(hour=s_hour, minute=s_minute, second=s_second, microsecond=0)
    end = now.replace(hour=e_hour, minute=e_minute, second=e_second, microsecond=0)

    if start <= now <= end:
        return True
    return False
