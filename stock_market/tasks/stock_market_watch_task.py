from celery import shared_task
import pandas as pd
import numpy as np
import jdatetime
from stock_market.utils import (
    MAIN_MARKET_TYPE_DICT,
    MAIN_PAPER_TYPE_DICT,
    MARKET_WATCH_COLUMN_RENAME,
    TSETMC_REQUEST_HEADERS,
    get_market_state,
)
from core.utils import (
    MongodbInterface,
    MARKET_STATE,
    task_timing,
    get_http_response,
    replace_arabic_letters_pd,
)
from core.models import FeatureToggle, ACTIVE
from core.configs import (
    TO_MILLION,
    RIAL_TO_BILLION_TOMAN,
    STOCK_DB,
    NO_DAILY_HISTORY,
    NO_HISTORY_DATE,
)
from tqdm import tqdm

from colorama import Fore, Style


def get_time(row):
    last_time = str(row.get("last_time"))
    if len(last_time) != 6:
        last_time = "0" + last_time
    last_time = f"{last_time[0:2]}:{last_time[2:4]}:{last_time[4:]}"

    return last_time


def calculate_buy_order_value(row):
    buy_orders = row.get("order_book")
    total_buy_value = 0
    for order_row in buy_orders:
        try:
            order_row_value = order_row["pmd"] * order_row["qmd"]
            total_buy_value += order_row_value
        except Exception:
            continue

    return total_buy_value


def calculate_sell_order_value(row):
    sell_orders = row.get("order_book")
    total_sell_value = 0
    for order_row in sell_orders:
        try:
            order_row_value = order_row["pmo"] * order_row["qmo"]
            total_sell_value += order_row_value
        except Exception:
            continue

    return total_sell_value


def add_link(row):
    ins_code = row.get("ins_code")
    link = f"https://www.tsetmc.com/instInfo/{ins_code}"

    return link


def update_market_watch_data(
    market_type: int, market_type_name: str, paper_type: int, paper_type_name: str
):
    URL = (
        "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"
        f"?market={market_type}&industrialGroup="
        f"&paperTypes%5B0%5D={paper_type}"
        "&showTraded=true&withBestLimits=true"
    )
    market_watch_df = get_http_response(req_url=URL, req_headers=TSETMC_REQUEST_HEADERS)
    try:
        market_watch_df = market_watch_df.json()
        market_watch_df = market_watch_df.get("marketwatch")
        market_watch_df = pd.DataFrame(market_watch_df)
    except Exception:
        market_watch_df = pd.DataFrame()

    URL = "https://cdn.tsetmc.com/api/ClientType/GetClientTypeAll"
    person_legal_df = get_http_response(req_url=URL, req_headers=TSETMC_REQUEST_HEADERS)
    try:
        person_legal_df = person_legal_df.json()
        person_legal_df = person_legal_df.get("clientTypeAllDto")
        person_legal_df = pd.DataFrame(person_legal_df)
    except Exception:
        person_legal_df = pd.DataFrame()

    if market_watch_df.empty or person_legal_df.empty:
        return

    merged_df = pd.merge(market_watch_df, person_legal_df, on="insCode", how="left")
    del market_watch_df
    del person_legal_df

    merged_df.rename(columns=MARKET_WATCH_COLUMN_RENAME, inplace=True)

    merged_df["last_time"] = merged_df.apply(get_time, axis=1)
    merged_df["last_date"] = str(jdatetime.date.today())

    merged_df["link"] = merged_df.apply(add_link, axis=1)

    merged_df["buy_pressure"] = (
        (
            (merged_df["person_buy_volume"] / merged_df["person_buy_count"])
            * merged_df["closing_price"]
        )
    ) / (
        (merged_df["person_sell_volume"] / merged_df["person_sell_count"])
        * merged_df["closing_price"]
    )

    merged_df["money_flow"] = (
        (merged_df["person_buy_volume"] - merged_df["person_sell_volume"])
        * merged_df["closing_price"]
    ) / RIAL_TO_BILLION_TOMAN

    merged_df["buy_value"] = (
        (merged_df["person_buy_volume"] * merged_df["closing_price"])
        / merged_df["person_buy_count"]
    ) / RIAL_TO_BILLION_TOMAN

    merged_df["buy_order_value"] = merged_df.apply(calculate_buy_order_value, axis=1)

    merged_df["buy_ratio"] = merged_df["buy_order_value"] / (
        merged_df["volume"] * merged_df["closing_price"]
    )

    merged_df["sell_order_value"] = merged_df.apply(calculate_sell_order_value, axis=1)

    merged_df["sell_ratio"] = merged_df["sell_order_value"] / (
        merged_df["volume"] * merged_df["closing_price"]
    )

    merged_df["person_buy_volume"] = merged_df["person_buy_volume"] / TO_MILLION
    merged_df["volume"] = merged_df["volume"] / TO_MILLION
    merged_df["base_volume"] = merged_df["base_volume"] / TO_MILLION
    merged_df["value"] = merged_df["value"] / RIAL_TO_BILLION_TOMAN
    merged_df["last_price_change"] = (
        merged_df["last_price_change"] / merged_df["yesterday_price"]
    ) * 100

    merged_df["closing_price_change"] = (
        merged_df["closing_price_change"] / merged_df["yesterday_price"]
    ) * 100

    merged_df["market_type"] = market_type
    merged_df["market_type_name"] = market_type_name
    merged_df["paper_type"] = paper_type
    merged_df["paper_type_name"] = paper_type_name

    return merged_df


def check_update_status(row):
    last_date = row.get("last_date")
    last_history_date = row.get("last_history_date")
    history = row.get("history")

    if last_date != last_history_date:
        return NO_DAILY_HISTORY
    return history


def get_history(row, index_name):
    new_time = row.get("last_time")
    index_value = round(row.get(index_name), 3)
    history = row.get("history")

    if history == NO_DAILY_HISTORY:
        history = list()
        history.append({"x": new_time, "y": index_value})
    else:
        time_set = set()
        for point in history:
            time_set.add(point["x"])

        if new_time not in time_set:
            history.append({"x": new_time, "y": index_value})

    return history


@task_timing
@shared_task(name="stock_market_watch_task")
def stock_market_watch():

    market_watch = pd.DataFrame()
    check_market_state = FeatureToggle.objects.get(name=MARKET_STATE["name"])
    for market_type_num, market_type_name in tqdm(
        MAIN_MARKET_TYPE_DICT.items(), desc="MarketWatch", ncols=10
    ):
        if check_market_state.state == ACTIVE:
            market_state = get_market_state(market_type_num)
            if market_state != check_market_state.value:
                print(Fore.RED + "Market is closed." + Style.RESET_ALL)
                continue

        for paper_type_num, paper_type_name in MAIN_PAPER_TYPE_DICT.items():
            watch_data = update_market_watch_data(
                market_type=market_type_num,
                market_type_name=market_type_name,
                paper_type=paper_type_num,
                paper_type_name=paper_type_name,
            )
            market_watch = pd.concat([market_watch, watch_data], axis=0)
            del watch_data

    if market_watch.empty:
        return

    market_watch.drop_duplicates(subset=["symbol"], keep="last", inplace=True)
    market_watch["name"] = market_watch.apply(
        replace_arabic_letters_pd, axis=1, args=("name",)
    )
    market_watch["symbol"] = market_watch.apply(
        replace_arabic_letters_pd, axis=1, args=("symbol",)
    )

    common_columns = [
        "ins_code",
        "link",
        "symbol",
        "name",
        "last_time",
        "last_date",
        "trade_count",
        "volume",
        "value",
        "closing_price",
        "closing_price_change",
        "last_price",
        "last_price_change",
        "market_type",
        "market_type_name",
        "paper_type",
        "paper_type_name",
    ]
    index_list = ["buy_pressure", "money_flow", "buy_value", "buy_ratio", "sell_ratio"]
    for index_name in tqdm(index_list, desc="Update indices", ncols=10):
        index_columns = common_columns + [index_name]
        index_df = market_watch[index_columns]

        index_df.loc[:, :] = index_df.replace([np.inf, -np.inf], np.nan)
        index_df = index_df.dropna()

        mongo_client = MongodbInterface(db_name=STOCK_DB, collection_name=index_name)
        history_df = list(mongo_client.collection.find({}, {"_id": 0}))
        history_df = pd.DataFrame(history_df)
        if history_df.empty:
            index_df["history"] = NO_DAILY_HISTORY
            index_df["last_history_date"] = NO_HISTORY_DATE
        else:
            history_df = history_df[["ins_code", "history", "last_date"]]
            history_df = history_df.rename(columns={"last_date": "last_history_date"})
            index_df = index_df.merge(right=history_df, on="ins_code", how="left")

        index_df["history"] = index_df["history"].replace(np.nan, NO_DAILY_HISTORY)
        index_df["last_history_date"] = index_df["last_history_date"].replace(
            np.nan, NO_HISTORY_DATE
        )

        index_df["history"] = index_df.apply(check_update_status, axis=1)
        index_df["history"] = index_df.apply(get_history, axis=1, args=(index_name,))
        index_df.drop("last_history_date", axis=1, inplace=True)
        index_df = index_df.to_dict(orient="records")

        mongo_client.insert_docs_into_collection(documents=index_df)
