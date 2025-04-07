import pandas as pd
import jdatetime as jdt
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface
from core.configs import (
    FIVE_MINUTES_CACHE,
    DASHBOARD_MONGO_DB,
    LAST_CLOSE_PRICE_COLLECTION,
)
from stock_market.utils import (
    STOCK_PAPER,
    INITIAL_MARKET_PAPER,
    PRIORITY_PAPER,
    FUND_PAPER,
    ETF_FUNDS_IG,
)


def add_last_close_price(row, industrial_group: int = None, paper_type: int = None):
    last_close = pd.DataFrame(row["last_close_price"])
    last_price_change = 0
    closing_price_change = 0

    if industrial_group:
        last_close = last_close[last_close["industrial_group"] == industrial_group]
    else:
        last_close = last_close[last_close["industrial_group"] != ETF_FUNDS_IG]

    if paper_type:
        last_close = last_close[last_close["paper_type"] == paper_type]
    else:
        last_close = last_close[
            last_close["paper_type"].isin(
                [STOCK_PAPER, INITIAL_MARKET_PAPER, PRIORITY_PAPER, FUND_PAPER]
            )
        ]

    if not last_close.empty:
        last_price_change = round(last_close["last_price_change"].mean(), 2)
        closing_price_change = round(last_close["closing_price_change"].mean(), 2)

    return pd.Series([last_price_change, closing_price_change])


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class LastClosePriceAPIView(APIView):
    def get(self, request):
        try:
            industrial_group = int(request.query_params.get("industrial_group"))
        except Exception:
            industrial_group = None
        try:
            paper_type = int(request.query_params.get("paper_type"))
        except Exception:
            paper_type = None

        mongo_conn = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=LAST_CLOSE_PRICE_COLLECTION
        )
        history_df = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

        history_df[["last_price_change", "closing_price_change"]] = history_df.apply(
            add_last_close_price, axis=1, args=(industrial_group, paper_type)
        )

        date = history_df.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "درصد قیمت آخرین و پایانی (غیر صندوق‌ها)"
        else:
            chart_title = f"درصد قیمت آخرین و پایانی {date} (غیر صندوق‌ها)"

        history_df.drop(["date", "last_close_price"], axis=1, inplace=True)

        history_df.rename(
            columns={
                "time": "x",
                "last_price_change": "y_1",
                "closing_price_change": "y_2",
            },
            inplace=True,
        )

        chart = {
            "x_title": "زمان",
            "y_1_title": "درصد قیمت آخرین",
            "y_2_title": "درصد قیمت پایانی",
            "chart_title": chart_title,
            "history": history_df.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
