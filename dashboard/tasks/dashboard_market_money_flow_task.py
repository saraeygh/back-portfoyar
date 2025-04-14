from uuid import uuid4

import jdatetime as jdt


from core.configs import (
    AUTO_MODE,
    MANUAL_MODE,
    RIAL_TO_BILLION_TOMAN,
    TO_BILLION,
    DASHBOARD_MONGO_DB,
    MARKET_MONEY_FLOW_COLLECTION,
    TEHRAN_TZ,
)
from core.utils import MongodbInterface, run_main_task

from fund.models import (
    FundInfo,
    UNKNOWN,
    FIXED_INCOME_FUND,
    MIXED_FUND,
    IN_STOCK_FUND,
    IN_STOCK_PARTIAL_FUND,
    IN_STOCK_LEVERAGE_FUND,
    IN_STOCK_INDEX_FUND,
)

from stock_market.utils import (
    STOCK_PAPER,
    PRIORITY_PAPER,
    is_in_schedule,
    get_market_watch_data_from_mongo,
)


def stock_priority_money_flow(market_watch):
    market_watch = market_watch[
        market_watch["paper_type"].isin([STOCK_PAPER, PRIORITY_PAPER])
    ]
    market_watch = market_watch[~market_watch["symbol"].str.contains(r"\d")]

    money_flow = [
        {
            "id": uuid4().hex,
            "name": "سهام و حق تقدم",
            "money_flow": round(market_watch["money_flow"].sum(), 2),
            "value": round(market_watch["value"].sum() / RIAL_TO_BILLION_TOMAN, 2),
            "volume": round(market_watch["volume"].sum() / TO_BILLION, 2),
        }
    ]

    return money_flow


def top_stocks_money_flow(market_watch):
    market_watch = market_watch[market_watch["paper_type"] == STOCK_PAPER]
    market_watch = market_watch[~market_watch["symbol"].str.contains(r"\d")]
    market_watch["market_cap"] = (
        market_watch["share_count"] * market_watch["closing_price"]
    )

    upper_stocks = market_watch.sort_values("market_cap", ascending=False).head(100)
    lower_stocks = market_watch.sort_values("market_cap", ascending=True).head(100)

    money_flow = [
        {
            "id": uuid4().hex,
            "name": "۱۰۰ نماد بزرگ",
            "money_flow": round(upper_stocks["money_flow"].sum(), 2),
            "value": round(upper_stocks["value"].sum() / RIAL_TO_BILLION_TOMAN, 2),
            "volume": round(upper_stocks["volume"].sum() / TO_BILLION, 2),
        },
        {
            "id": uuid4().hex,
            "name": "۱۰۰ نماد کوچک",
            "money_flow": round(lower_stocks["money_flow"].sum(), 2),
            "value": round(lower_stocks["value"].sum() / RIAL_TO_BILLION_TOMAN, 2),
            "volume": round(lower_stocks["volume"].sum() / TO_BILLION, 2),
        },
    ]

    return money_flow


def get_fund_money_flow(fund_type_code, fund_type_name, market_watch):
    funds = list(
        FundInfo.objects.filter(fund_type__code=fund_type_code)
        .exclude(ins_code=UNKNOWN)
        .values_list("ins_code", flat=True)
    )

    funds = market_watch[market_watch["ins_code"].isin(funds)]

    money_flow = [
        {
            "id": uuid4().hex,
            "name": fund_type_name,
            "money_flow": round(funds["money_flow"].sum(), 2),
            "value": round(funds["value"].sum() / RIAL_TO_BILLION_TOMAN, 2),
            "volume": round(funds["volume"].sum() / TO_BILLION, 2),
        }
    ]

    return money_flow


def funds_money_flow(market_watch):
    fund_types = {
        FIXED_INCOME_FUND: "صندوق‌های درآمد ثابت",
        MIXED_FUND: "صنذوق‌های مختلط",
        IN_STOCK_FUND: "صندوق‌های سهامی",
        IN_STOCK_PARTIAL_FUND: "صندوق‌های بخشی",
        IN_STOCK_LEVERAGE_FUND: "صندوق‌های اهرمی",
        IN_STOCK_INDEX_FUND: "صندوق‌های شاخصی",
        # VENTURE_CAPITAL_FUND: "صندوق‌های  جسورانه",
    }

    money_flow = []
    for fund_type_code, fund_type_name in fund_types.items():
        money_flow += get_fund_money_flow(fund_type_code, fund_type_name, market_watch)

    return money_flow


def check_date():
    today_datetime = jdt.datetime.now(tz=TEHRAN_TZ)
    date = today_datetime.strftime("%Y/%m/%d")
    time = today_datetime.strftime("%H:%M")

    mongo_conn = MongodbInterface(
        db_name=DASHBOARD_MONGO_DB, collection_name=MARKET_MONEY_FLOW_COLLECTION
    )

    one_doc = mongo_conn.collection.find_one({}, {"_id": 0})
    if one_doc and one_doc["date"] != date:
        mongo_conn.collection.delete_many({})

    return date, time


def dashboard_market_money_flow_main(run_mode: str):
    if run_mode == MANUAL_MODE or is_in_schedule(8, 59, 0, 12, 40, 0):
        market_watch = get_market_watch_data_from_mongo()
        market_watch["money_flow"] = (
            (
                market_watch["individual_buy_volume"]
                - market_watch["individual_sell_volume"]
            )
            * market_watch["closing_price"]
        ) / RIAL_TO_BILLION_TOMAN
        market_watch = market_watch[
            [
                "ins_code",
                "symbol",
                "paper_type",
                "closing_price",
                "share_count",
                "value",
                "volume",
                "money_flow",
            ]
        ]

        result = []
        result += stock_priority_money_flow(market_watch)
        result += top_stocks_money_flow(market_watch)
        result += funds_money_flow(market_watch)

        date, time = check_date()
        doc = {"date": date, "time": time, "result": result}

        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=MARKET_MONEY_FLOW_COLLECTION
        )
        mongo_conn.collection.insert_one(doc)


def dashboard_market_money_flow(run_mode: str = AUTO_MODE):

    run_main_task(
        main_task=dashboard_market_money_flow_main,
        kw_args={"run_mode": run_mode},
    )
