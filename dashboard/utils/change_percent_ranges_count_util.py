import math
import jdatetime as jdt

from core.utils import MongodbInterface
from core.configs import DASHBOARD_MONGO_DB, CHANGE_PERCENT_RANGES, TEHRAN_TZ

from stock_market.utils import (
    STOCK_PAPER,
    PRIORITY_PAPER,
    FUND_PAPER,
    get_market_watch_data_from_mongo,
)

from fund.models import (
    FundInfo,
    UNKNOWN,
    IN_STOCK_FUND,
    IN_STOCK_PARTIAL_FUND,
    IN_STOCK_LEVERAGE_FUND,
    IN_STOCK_INDEX_FUND,
)


def get_in_stock_funds_list():
    in_stock_funds = list(
        FundInfo.objects.filter(
            fund_type__code__in=[
                IN_STOCK_FUND,
                IN_STOCK_PARTIAL_FUND,
                IN_STOCK_LEVERAGE_FUND,
                IN_STOCK_INDEX_FUND,
            ],
        )
        .exclude(ins_code=UNKNOWN)
        .values_list("ins_code", flat=True)
    )

    return in_stock_funds


def get_date_time():
    today_datetime = jdt.datetime.now(tz=TEHRAN_TZ)
    date = today_datetime.strftime("%Y/%m/%d")
    time = today_datetime.strftime("%H:%M")

    return date, time


def get_correct_sign(number):
    if number < 0:
        return f"{abs(number)}٪-"
    elif number > 0:
        return f"{abs(number)}٪"
    else:
        return f"{number}"


def change_percent_ranges_count():
    percent_ranges = get_market_watch_data_from_mongo()
    if not percent_ranges.empty:
        percent_ranges["daily_roi"] = (
            percent_ranges["last_price_change"] / percent_ranges["yesterday_price"]
        ) * 100
        percent_ranges = percent_ranges[["ins_code", "paper_type", "daily_roi"]]

        in_stock_funds_list = get_in_stock_funds_list()
        percent_ranges = percent_ranges[
            (percent_ranges["paper_type"].isin([STOCK_PAPER, PRIORITY_PAPER]))
            | (
                (percent_ranges["paper_type"] == FUND_PAPER)
                & (percent_ranges["ins_code"].isin(in_stock_funds_list))
            )
        ]

        range_min = math.floor(percent_ranges["daily_roi"].min())
        range_max = math.floor(percent_ranges["daily_roi"].max()) + 1

        range_left = range_min
        result = []
        for _ in range(abs(range_max - range_min)):
            range_right = range_left + 1

            range_rows = len(
                percent_ranges[
                    (percent_ranges["daily_roi"] >= range_left)
                    & (percent_ranges["daily_roi"] < range_right)
                ]
            )

            result.append(
                {
                    "range": f"({get_correct_sign(range_right)}, {get_correct_sign(range_left)})",
                    "count": range_rows,
                }
            )

            range_left += 1

            if range_right == range_max:
                break

        date, time = get_date_time()
        doc = [
            {
                "date": date,
                "time": time,
                "change_percent_ranges": result,
            }
        ]

        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=CHANGE_PERCENT_RANGES
        )
        mongo_conn.insert_docs_into_collection(doc)
