from celery import shared_task
import pandas as pd

from core.utils import (
    RedisInterface,
    is_scheduled,
    task_timing,
    get_http_response,
    replace_arabic_letters_pd,
)
from core.configs import (
    MARKET_WATCH_URL,
    CLIENT_TYPE_URL,
    STOCK_REDIS_DB,
    MARKET_WATCH_REDIS_KEY,
)

from stock_market.models import StockInstrument
from stock_market.utils import (
    TSETMC_REQUEST_HEADERS,
    MARKET_WATCH_COLS,
    INDIVIDUAL_LEGAL_COLS,
    is_market_open,
)
from colorama import Fore, Style


def get_market_watch():
    market_watch = get_http_response(
        req_url=MARKET_WATCH_URL, req_headers=TSETMC_REQUEST_HEADERS
    )
    market_watch = market_watch.json()
    market_watch = market_watch.get("marketwatch")
    market_watch = pd.DataFrame(market_watch)
    market_watch.rename(columns=MARKET_WATCH_COLS, inplace=True)
    market_watch = market_watch[list(MARKET_WATCH_COLS.values())]

    return market_watch


def get_client_type():
    client_type = get_http_response(
        req_url=CLIENT_TYPE_URL, req_headers=TSETMC_REQUEST_HEADERS
    )
    client_type = client_type.json()
    client_type = client_type.get("clientTypeAllDto")
    client_type = pd.DataFrame(client_type)
    client_type.rename(columns=INDIVIDUAL_LEGAL_COLS, inplace=True)
    client_type = client_type[list(INDIVIDUAL_LEGAL_COLS.values())]

    return client_type


def get_additional_info():
    additional_info = StockInstrument.objects.all().values(
        "ins_code", "market_type", "paper_type", "industrial_group"
    )
    additional_info = pd.DataFrame(additional_info)

    return additional_info


redis_conn = RedisInterface(db=STOCK_REDIS_DB)


@task_timing
@shared_task(name="update_market_watch_task")
def update_market_watch():

    if not is_scheduled(weekdays=[0, 1, 2, 3, 4], start=8, end=19):
        return

    if not is_market_open():
        return

    additional_info = get_additional_info()
    market_watch = get_market_watch()
    market_watch = pd.merge(
        left=market_watch, right=additional_info, on="ins_code", how="left"
    )
    del additional_info

    client_type = get_client_type()
    market_watch = pd.merge(
        left=market_watch, right=client_type, on="ins_code", how="left"
    )
    del client_type
    market_watch.dropna(inplace=True)

    if market_watch.empty:
        print(Fore.RED + "No market watch data!" + Style.RESET_ALL)
        return

    market_watch["name"] = market_watch.apply(
        replace_arabic_letters_pd, axis=1, args=("name",)
    )
    market_watch["symbol"] = market_watch.apply(
        replace_arabic_letters_pd, axis=1, args=("symbol",)
    )

    market_watch = market_watch.to_dict(orient="records")
    redis_conn.bulk_push_list_of_dicts(
        list_key=MARKET_WATCH_REDIS_KEY, list_of_dicts=market_watch
    )

    print(Fore.GREEN + "Market watch updated" + Style.RESET_ALL)
