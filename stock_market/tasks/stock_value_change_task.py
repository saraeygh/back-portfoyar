import jdatetime
import pandas as pd

from core.models import FeatureToggle
from core.configs import STOCK_DB, RIAL_TO_BILLION_TOMAN, TO_MILLION
from core.utils import (
    MongodbInterface,
    task_timing,
    get_http_response,
    replace_arabic_letters_pd,
)
from stock_market.utils import (
    MAIN_MARKET_TYPE_DICT,
    MAIN_PAPER_TYPE_DICT,
    TSETMC_REQUEST_HEADERS,
    VOLUME_CHANGE_DICT,
    get_market_state,
)
from celery import shared_task
from tqdm import tqdm
from colorama import Fore, Style


def add_last_update(row):
    last_update = str(row.get("last_update"))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def add_today_to_history(row, last_date):
    history = list(row.get("history"))
    value = int(row.get("value"))
    history.append({"x": last_date, "y": value})

    return history


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


@task_timing
@shared_task(name="stock_value_change_task")
def stock_value_change():

    value_change = pd.DataFrame()
    check_market_state = FeatureToggle.objects.get(name="market_state")
    for market_type, market_type_name in tqdm(MAIN_MARKET_TYPE_DICT.items()):
        if check_market_state.state == 1:
            market_state = get_market_state(market_type)
            if market_state != check_market_state.value:
                print(Fore.RED + "market is closed!" + Style.RESET_ALL)
                continue

        for paper_type, paper_type_name in MAIN_PAPER_TYPE_DICT.items():
            MARKET_WATCH_URL = (
                "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"
                f"?market={market_type}&industrialGroup="
                f"&paperTypes%5B0%5D={paper_type}"
                "&showTraded=true&withBestLimits=true"
            )

            last_data = get_http_response(
                req_url=MARKET_WATCH_URL, req_headers=TSETMC_REQUEST_HEADERS
            )
            try:
                last_data = last_data.json()
                last_data = last_data.get("marketwatch")
                last_data = pd.DataFrame(last_data)

                last_data = last_data.rename(columns=VOLUME_CHANGE_DICT)
                last_data = last_data[list(VOLUME_CHANGE_DICT.values())]
                last_data["name"] = last_data.apply(
                    replace_arabic_letters_pd, axis=1, args=("name",)
                )
                last_data["symbol"] = last_data.apply(
                    replace_arabic_letters_pd, axis=1, args=("symbol",)
                )
            except Exception:
                continue

            mongo_client = MongodbInterface(db_name=STOCK_DB, collection_name="history")
            history = list(mongo_client.collection.find({}, {"_id": 0}))
            history = pd.DataFrame(history)

            last_data = last_data.merge(right=history, on="ins_code", how="left")
            del history

            last_data["last_price_change"] = (
                last_data["last_price_change"] / last_data["yesterday_price"]
            ) * 100
            last_data["closing_price_change"] = (
                last_data["closing_price_change"] / last_data["yesterday_price"]
            ) * 100
            last_data["value_change"] = last_data["value"] / last_data["mean"]

            last_date = str(jdatetime.date.today())
            last_data["last_update"] = last_data.apply(add_last_update, axis=1)

            last_data.dropna(inplace=True)
            if last_data.empty:
                continue

            last_data["value"] = last_data["value"] / RIAL_TO_BILLION_TOMAN
            last_data["mean"] = last_data["mean"] / RIAL_TO_BILLION_TOMAN
            last_data["volume"] = last_data["volume"] / TO_MILLION
            last_data["link"] = last_data.apply(add_link, axis=1)

            last_data["history"] = last_data.apply(
                add_today_to_history, axis=1, args=(last_date,)
            )

            last_data["market_type"] = market_type
            last_data["market_type_name"] = market_type_name
            last_data["paper_type"] = paper_type
            last_data["paper_type_name"] = paper_type_name

            value_change = pd.concat([value_change, last_data])

    if value_change.empty:
        return

    value_change.drop_duplicates(subset=["symbol"], keep="last", inplace=True)
    value_change = value_change.to_dict(orient="records")

    mongo_client.collection = mongo_client.db["value_change"]
    mongo_client.insert_docs_into_collection(documents=value_change)
