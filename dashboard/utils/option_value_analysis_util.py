from datetime import datetime as dt
import jdatetime as jdt
import pandas as pd
from core.utils import MongodbInterface
from core.configs import (
    DASHBOARD_MONGO_DB,
    OPTION_VALUE_ANALYSIS_COLLECTION,
    RIAL_TO_BILLION_TOMAN,
    MILLION_TO_BILLION_TOMAN,
)

from option_market.utils import get_option_data_from_mongo
from option_market.models import OptionValue

from stock_market.utils import (
    STOCK_PAPER,
    INITIAL_MARKET_PAPER,
    PRIORITY_PAPER,
    get_market_watch_data_from_mongo,
)


def convert_date(row):
    g_date = row.get("date")

    j_date = jdt.date.fromgregorian(date=g_date)
    j_date = j_date.strftime("%Y/%m/%d")

    return j_date


def get_today_data():
    market_watch = get_market_watch_data_from_mongo()

    market_value = market_watch[
        market_watch["paper_type"].isin(
            [STOCK_PAPER, INITIAL_MARKET_PAPER, PRIORITY_PAPER]
        )
    ]["value"].sum()

    option_data = get_option_data_from_mongo()

    call_value = option_data["call_value"].sum()
    put_value = option_data["put_value"].sum()
    option_value = call_value + put_value
    put_to_call = put_value / call_value

    new_doc = [
        {
            "date": dt.today().date(),
            "call_value": round(call_value / RIAL_TO_BILLION_TOMAN, 3),
            "put_value": round(put_value / RIAL_TO_BILLION_TOMAN, 3),
            "option_value": round(option_value / RIAL_TO_BILLION_TOMAN, 3),
            "put_to_call": round(put_to_call, 3),
            "option_to_market": round(option_value / market_value, 3),
        }
    ]

    return pd.DataFrame(new_doc)


def option_value_analysis():
    data_history = pd.DataFrame(
        OptionValue.objects.order_by("-date").values(
            "date",
            "call_value",
            "put_value",
            "option_value",
            "put_to_call",
            "option_to_market",
        )[0:90]
    )
    data_history = data_history.sort_values(by="date")

    data_history["call_value"] = data_history["call_value"].astype(float)
    data_history["put_value"] = data_history["put_value"].astype(float)
    data_history["option_value"] = data_history["option_value"].astype(float)
    data_history["put_to_call"] = data_history["put_to_call"].astype(float)
    data_history["option_to_market"] = data_history["option_to_market"].astype(float)

    data_history["call_value"] = round(
        data_history["call_value"] / MILLION_TO_BILLION_TOMAN, 3
    )
    data_history["put_value"] = round(
        data_history["put_value"] / MILLION_TO_BILLION_TOMAN, 3
    )
    data_history["option_value"] = round(
        data_history["option_value"] / MILLION_TO_BILLION_TOMAN, 3
    )

    today_data = get_today_data()

    all_history = pd.concat([data_history, today_data])
    all_history["date"] = all_history.apply(convert_date, axis=1)
    all_history = all_history.to_dict(orient="records")

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=OPTION_VALUE_ANALYSIS_COLLECTION
    )

    mongo_conn.insert_docs_into_collection(all_history)
