from datetime import date
import pandas as pd
from colorama import Fore, Style

from core.utils import (
    MongodbInterface,
    MARKET_WATCH_URL,
    CLIENT_TYPE_URL,
    TSETMC_REQUEST_HEADERS,
    get_http_response,
    replace_arabic_letters_pd,
    run_main_task,
)
from core.configs import (
    AUTO_MODE,
    MANUAL_MODE,
    STOCK_MONGO_DB,
    MARKET_WATCH_COLLECTION,
)

from stock_market.models import StockInstrument
from stock_market.utils import (
    MARKET_WATCH_COLS,
    INDIVIDUAL_LEGAL_COLS,
    is_market_open,
)


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
        "ins_code", "market_type", "paper_type", "industrial_group__code"
    )
    additional_info = pd.DataFrame(additional_info)
    additional_info.rename(
        columns={"industrial_group__code": "industrial_group"}, inplace=True
    )

    return additional_info


def update_market_watch_main(run_mode):
    if run_mode == MANUAL_MODE or is_market_open():
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

        market_watch["market_type"] = market_watch["market_type"].astype(int)
        market_watch["paper_type"] = market_watch["paper_type"].astype(int)
        market_watch["last_date"] = date.today().strftime("%Y-%m-%d")
        market_watch = market_watch.to_dict(orient="records")
        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name=MARKET_WATCH_COLLECTION
        )
        mongo_conn.insert_docs_into_collection(market_watch)


def update_market_watch(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=update_market_watch_main,
        kw_args={"run_mode": run_mode},
    )
