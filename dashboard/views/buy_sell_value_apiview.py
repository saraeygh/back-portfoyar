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
    BUY_SELL_ORDERS_COLLECTION,
    RIAL_TO_BILLION_TOMAN,
)

FUNDS_INDUSTRIAL_GROUP = 68


def add_buy_sell_values(row, industrial_group: int = None, paper_type: int = None):
    order_book = pd.DataFrame(row["order_book_value"])
    buy_value = 0
    sell_value = 0

    if industrial_group:
        order_book = order_book[order_book["industrial_group"] == industrial_group]
    else:
        order_book = order_book[
            ~order_book["industrial_group"] == FUNDS_INDUSTRIAL_GROUP
        ]

    if paper_type:
        order_book = order_book[order_book["paper_type"] == paper_type]
    else:
        order_book = order_book[order_book["paper_type"].isin([1, 2, 8, 4])]

    if not order_book.empty:
        buy_value = int(order_book["buy_value"].sum() / RIAL_TO_BILLION_TOMAN)
        sell_value = int(order_book["sell_value"].sum() / RIAL_TO_BILLION_TOMAN)

    return pd.Series([buy_value, sell_value])


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class BuySellValueAPIView(APIView):
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
            db_name=DASHBOARD_MONGO_DB, collection_name=BUY_SELL_ORDERS_COLLECTION
        )
        history_df = pd.DataFrame(mongo_conn.collection.find({}, {"_id": 0}))

        history_df[["buy_value", "sell_value"]] = history_df.apply(
            add_buy_sell_values, axis=1, args=(industrial_group, paper_type)
        )

        date = history_df.iloc[0].get("date")

        today_date = jdt.date.today().strftime("%Y/%m/%d")
        if date == today_date:
            chart_title = "تغییرات امروز ارزش سفارش‌های خرید و فروش پنج خط اول"
        else:
            chart_title = (
                f"تغییرات ارزش سفارش‌های خرید و فروش پنج خط اول به تاریخ {date}"
            )

        history_df.drop(["date", "order_book_value"], axis=1, inplace=True)

        history_df.rename(
            columns={"time": "x", "buy_value": "y_1", "sell_value": "y_2"}, inplace=True
        )

        chart = {
            "x_title": "زمان",
            "y_1_title": "ارزش سفارش‌های خرید (میلیارد تومان)",
            "y_2_title": "ارزش سفارش‌های فروش (میلیارد تومان)",
            "chart_title": chart_title,
            "history": history_df.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
