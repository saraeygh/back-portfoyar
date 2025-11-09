from celery import shared_task

import jdatetime as jdt
import pandas as pd

from core.configs import (
    STOCK_OPTION_STRIKE_DEVIATION,
    STOCK_MONGO_DB,
    AUTO_MODE,
    MANUAL_MODE,
    RIAL_TO_MILLION_TOMAN,
    TEHRAN_TZ,
    OPTION_MONGO_DB,
    OPTION_DATA_COLLECTION,
)
from core.utils import (
    MongodbInterface,
    get_deviation_percent,
    run_main_task,
    is_market_open_today,
)

from option_market.utils import (
    COMMON_OPTION_COLUMN,
    BASE_EQUITY_COLUMNS,
    CALL_OPTION_COLUMN,
    PUT_OPTION_COLUMN,
)
from stock_market.utils import CALL_OPTION, PUT_OPTION, is_in_schedule


CALL_OLD_NEW_MAPPING = {
    "call_ins_code": "inst_id",
    "option_link": "option_link",
    "stock_link": "stock_link",
    "call_last_update": "last_update",
    "call_symbol": "symbol",
    "base_equity_symbol": "asset_name",
    "base_equity_last_price": "base_equit_price",
    "strike_price": "strike",
    "monthly_price_spread": "monthly_price_spread",
    "remained_day": "days_to_expire",
    "price_spread": "price_spread",
    "end_date": "expiration_date",
    "option_type": "option_type",
    "call_value": "value",
    "call_best_sell_price": "premium",
    "strike_premium": "strike_premium",
    "strike_deviation": "strike_deviation",
}

PUT_OLD_NEW_MAPPING = {
    "put_ins_code": "inst_id",
    "option_link": "option_link",
    "stock_link": "stock_link",
    "put_last_update": "last_update",
    "put_symbol": "symbol",
    "base_equity_symbol": "asset_name",
    "base_equity_last_price": "base_equit_price",
    "strike_price": "strike",
    "monthly_price_spread": "monthly_price_spread",
    "remained_day": "days_to_expire",
    "price_spread": "price_spread",
    "end_date": "expiration_date",
    "option_type": "option_type",
    "put_value": "value",
    "put_best_buy_price": "premium",
    "strike_premium": "strike_premium",
    "strike_deviation": "strike_deviation",
}


def get_last_options():
    mongo_conn = MongodbInterface(
        db_name=OPTION_MONGO_DB, collection_name=OPTION_DATA_COLLECTION
    )
    last_options = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

    return last_options


def strike_deviation(row):
    strike = int(row.get("strike_price"))
    asset_price = int(row.get("base_equity_last_price"))

    try:
        deviation = get_deviation_percent(strike, asset_price)
    except Exception:
        deviation = 0

    return deviation


def add_strike_premium(row, option_type):
    strike = int(row.get("strike_price"))
    if option_type == CALL_OPTION:
        premium = int(row.get("call_best_sell_price"))
    else:
        premium = int(row.get("put_best_buy_price"))

    return strike + premium


def add_price_spread(row):
    strike_premium = int(row.get("strike_premium"))
    asset_price = int(row.get("base_equity_last_price"))

    try:
        spread = get_deviation_percent(strike_premium, asset_price)
    except Exception:
        spread = 0

    return spread


def monthly_price_spread(row):
    remained_days = int(row.get("remained_day"))
    price_spread = int(row.get("price_spread"))

    try:
        monthly_spread = (price_spread / remained_days) * 30
    except Exception:
        monthly_spread = 0

    return monthly_spread


def add_stock_link(row):
    ins_code = str(row.get("base_equity_ins_code"))
    link = f"https://main.tsetmc.com/InstInfo/{ins_code}/"

    return link


def add_option_link(row, option_type):
    if option_type == CALL_OPTION:
        ins_code = str(row.get("call_ins_code"))
    else:
        ins_code = str(row.get("put_ins_code"))
    link = f"https://main.tsetmc.com/InstInfo/{ins_code}/"

    return link


def edit_last_update(row):
    last_update = str(int(row.get("last_update")))
    if len(last_update) != 6:
        last_update = "0" + last_update
    last_update = f"{last_update[0:2]}:{last_update[2:4]}:{last_update[4:]}"

    return last_update


def get_call_spreads(spreads):
    results = []
    spreads = spreads[
        list(COMMON_OPTION_COLUMN.values())
        + list(BASE_EQUITY_COLUMNS.values())
        + list(CALL_OPTION_COLUMN.values())
        + ["call_last_update", "base_equity_last_update"]
    ]
    spreads = spreads.loc[
        (spreads["call_last_update"] > 90000)
        & (spreads["base_equity_last_update"] > 90000)
        & (spreads["call_yesterday_price"] > 0)
    ]

    if not spreads.empty:
        spreads["strike_deviation"] = spreads.apply(strike_deviation, axis=1)
        spreads = spreads[
            abs(spreads["strike_deviation"]) < STOCK_OPTION_STRIKE_DEVIATION
        ]
        if not spreads.empty:
            spreads["strike_premium"] = spreads.apply(
                add_strike_premium, axis=1, args=(CALL_OPTION,)
            )

            spreads["price_spread"] = spreads.apply(add_price_spread, axis=1)

            spreads["monthly_price_spread"] = spreads.apply(
                monthly_price_spread, axis=1
            )

            spreads["stock_link"] = spreads.apply(add_stock_link, axis=1)
            spreads["option_link"] = spreads.apply(
                add_option_link, axis=1, args=(CALL_OPTION,)
            )

            spreads["option_type"] = "اختیار خرید"

            spreads.dropna(inplace=True)
            spreads["last_price"] = spreads["call_last_price"]
            spreads["last_price_change"] = (
                (spreads["call_last_price"] - spreads["call_yesterday_price"])
                / spreads["call_yesterday_price"]
            ) * 100
            spreads = spreads.rename(columns=CALL_OLD_NEW_MAPPING)
            spreads = spreads[
                list(CALL_OLD_NEW_MAPPING.values())
                + ["last_price", "last_price_change"]
            ]
            spreads["last_update"] = spreads.apply(edit_last_update, axis=1)
            spreads["value"] = spreads["value"] / RIAL_TO_MILLION_TOMAN
            results = spreads.to_dict(orient="records")

    return results


def get_put_spreads(spreads):
    results = []
    spreads = spreads[
        list(COMMON_OPTION_COLUMN.values())
        + list(BASE_EQUITY_COLUMNS.values())
        + list(PUT_OPTION_COLUMN.values())
        + ["put_last_update", "base_equity_last_update"]
    ]
    spreads = spreads.loc[
        (spreads["put_last_update"] > 90000)
        & (spreads["base_equity_last_update"] > 90000)
        & (spreads["put_yesterday_price"] > 0)
    ]

    if not spreads.empty:
        spreads["strike_deviation"] = spreads.apply(strike_deviation, axis=1)
        spreads = spreads[
            abs(spreads["strike_deviation"]) < STOCK_OPTION_STRIKE_DEVIATION
        ]
        if not spreads.empty:
            spreads["strike_premium"] = spreads.apply(
                add_strike_premium, axis=1, args=(PUT_OPTION,)
            )

            spreads["price_spread"] = spreads.apply(add_price_spread, axis=1)

            spreads["monthly_price_spread"] = spreads.apply(
                monthly_price_spread, axis=1
            )

            spreads["stock_link"] = spreads.apply(add_stock_link, axis=1)
            spreads["option_link"] = spreads.apply(
                add_option_link, axis=1, args=(PUT_OPTION,)
            )

            spreads["option_type"] = "اختیار فروش"

            spreads.dropna(inplace=True)
            spreads["last_price"] = spreads["put_last_price"]
            spreads["last_price_change"] = (
                (spreads["put_last_price"] - spreads["put_yesterday_price"])
                / spreads["put_yesterday_price"]
            ) * 100
            spreads = spreads.rename(columns=PUT_OLD_NEW_MAPPING)
            spreads = spreads[
                list(PUT_OLD_NEW_MAPPING.values()) + ["last_price", "last_price_change"]
            ]
            spreads["last_update"] = spreads.apply(edit_last_update, axis=1)
            spreads["value"] = spreads["value"] / RIAL_TO_MILLION_TOMAN
            results = spreads.to_dict(orient="records")

    return results


def check_date(mongo_conn):
    today_datetime = jdt.datetime.now(tz=TEHRAN_TZ)
    date = today_datetime.strftime("%Y/%m/%d")
    time = today_datetime.strftime("%H:%M")

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc:
        doc_date = one_doc.get("date")
        if date != doc_date:
            mongo_conn.collection.delete_many({})

    return date, time


X_TITLE = "زمان"
Y_TITLE = "اسپرد قیمتی"
CHART_TITLE = "روند تغییرات روزانه اسپرد قیمتی"


def add_last_spread_to_history(row):
    row = row.to_dict()
    chart = row.get("chart")
    x = row.get("last_update")
    y = row.get("price_spread")

    if isinstance(chart, dict):
        history: list = chart.get("history")
        last_history = history[-1]
        if x != last_history["x"]:
            history.append({"x": x, "y": round(y, 3)})
            chart["history"] = history
            return chart

    else:
        chart = {
            "x_title": X_TITLE,
            "y_title": Y_TITLE,
            "chart_title": CHART_TITLE,
            "history": [{"x": x, "y": round(y, 3)}],
        }

    return chart


def add_spread_history(mongo_client, last_spreads):
    try:
        spread_history = pd.DataFrame(
            mongo_client.collection.find(
                {},
                {"_id": 0, "inst_id": 1, "chart": 1},
            )
        )
        if not spread_history.empty:
            last_spreads = pd.merge(
                left=last_spreads, right=spread_history, on="inst_id", how="left"
            )
    except Exception:
        pass

    last_spreads["chart"] = last_spreads.apply(add_last_spread_to_history, axis=1)

    return last_spreads


def stock_option_price_spread_main(run_mode):
    if (
        is_in_schedule(9, 2, 0, 12, 40, 0) and is_market_open_today()
    ) or run_mode == MANUAL_MODE:
        spreads = get_last_options()
        last_spreads = pd.DataFrame()
        if not spreads.empty:
            call_spreads = get_call_spreads(spreads)
            put_spreads = get_put_spreads(spreads)
            last_spreads = pd.DataFrame(call_spreads + put_spreads)

        if not last_spreads.empty:
            mongo_conn = MongodbInterface(
                db_name=STOCK_MONGO_DB, collection_name="option_price_spread"
            )
            last_spreads["date"], _ = check_date(mongo_conn)
            last_spreads = add_spread_history(mongo_conn, last_spreads)

            last_spreads = last_spreads.to_dict(orient="records")
            mongo_conn.insert_docs_into_collection(documents=last_spreads)


@shared_task(name="stock_option_price_spread_task", expires=60)
def stock_option_price_spread(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=stock_option_price_spread_main,
        kw_args={"run_mode": run_mode},
    )
