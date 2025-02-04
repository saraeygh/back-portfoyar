import pandas as pd
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


def get_buy_sell_value(
    order_book: pd.DataFrame, industrial_group: int = None, paper_type: int = None
):
    buy_sell_value = {
        "buy_value": 0,
        "sell_value": 0,
    }

    if industrial_group:
        order_book = order_book[order_book["industrial_group"] == industrial_group]

    if paper_type:
        order_book = order_book[order_book["paper_type"] == paper_type]
    else:
        order_book = order_book[order_book["paper_type"].isin([1, 2, 8, 4])]

    if not order_book.empty:
        buy_sell_value["buy_value"] = int(
            order_book["buy_value"].sum() / RIAL_TO_BILLION_TOMAN
        )
        buy_sell_value["sell_value"] = int(
            order_book["sell_value"].sum() / RIAL_TO_BILLION_TOMAN
        )

    return buy_sell_value


def add_buy_sell_values(row, industrial_group: int = None, paper_type: int = None):
    order_book = pd.DataFrame(row["order_book_value"])
    buy_value = 0
    sell_value = 0

    if industrial_group:
        order_book = order_book[order_book["industrial_group"] == industrial_group]

    if paper_type:
        order_book = order_book[order_book["paper_type"] == paper_type]
    else:
        order_book = order_book[order_book["paper_type"].isin([1, 2, 8, 4])]

    if not order_book.empty:
        buy_value = int(order_book["buy_value"].sum() / RIAL_TO_BILLION_TOMAN)
        sell_value = int(order_book["sell_value"].sum() / RIAL_TO_BILLION_TOMAN)

    return pd.Series([buy_value, sell_value])


# @method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
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

        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=BUY_SELL_ORDERS_COLLECTION
        )

        history_df = pd.DataFrame(mongo_client.collection.find({}, {"_id": 0}))
        history_df[["buy_value", "sell_value"]] = history_df.apply(
            add_buy_sell_values, axis=1, args=(industrial_group, paper_type)
        )
        history_df.drop("order_book_value", axis=1, inplace=True)

        return Response(history_df.to_dict(orient="records"), status=status.HTTP_200_OK)
