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
    LAST_CLOSE_PRICE_COLLECTION,
)


def get_last_close_price(
    last_close: pd.DataFrame, industrial_group: int = None, paper_type: int = None
):
    last_close_price = {
        "last_price_change": 0,
        "close_price_change": 0,
    }

    if industrial_group:
        last_close = last_close[last_close["industrial_group"] == industrial_group]

    if paper_type:
        last_close = last_close[last_close["paper_type"] == paper_type]
    else:
        last_close = last_close[last_close["paper_type"].isin([1, 2, 8, 4])]

    if not last_close.empty:
        last_close_price["last_price_change"] = round(
            last_close["last_price_change"].mean(), 2
        )
        last_close_price["close_price_change"] = round(
            last_close["close_price_change"].mean(), 2
        )

    return last_close_price


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

        mongo_client = MongodbInterface(
            db_name=DASHBOARD_MONGO_DB, collection_name=LAST_CLOSE_PRICE_COLLECTION
        )

        history_list = list(mongo_client.collection.find({}, {"_id": 0}))
        last_close_price = list()
        if history_list:
            for history in history_list:
                result = get_last_close_price(
                    pd.DataFrame(history["last_close_price"]),
                    industrial_group,
                    paper_type,
                )
                last_close_price.append(
                    {"date": history["date"], "time": history["time"], **result}
                )

        return Response(last_close_price, status=status.HTTP_200_OK)
