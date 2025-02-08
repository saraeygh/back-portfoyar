import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.utils import MongodbInterface
from core.configs import GLOBAL_MONGO_DB, DASHBOARD_TOP_5_LIMIT, THIRTY_MINUTES_CACHE

from global_market.serializers import DashboardGlobalMeanDeviationSerailizer


PRICE_CHANGES_POS = "inc"
PRICE_CHANGES_NEG = "dec"


def get_range_result(collection_name, price_changes):
    default_range_result = []

    mongo_client = MongodbInterface(
        db_name=GLOBAL_MONGO_DB, collection_name=collection_name
    )

    if price_changes == PRICE_CHANGES_POS:
        range_result = list(
            mongo_client.collection.find({"deviation": {"$gte": 0}}, {"_id": 0})
        )
    else:
        range_result = list(
            mongo_client.collection.find({"deviation": {"$lt": 0}}, {"_id": 0})
        )

    range_result = pd.DataFrame(range_result)
    if range_result.empty:
        return default_range_result

    if price_changes == PRICE_CHANGES_POS:
        range_result = range_result.sort_values(by="deviation", ascending=False)
    else:
        range_result = range_result.sort_values(by="deviation", ascending=True)

    range_result = range_result.head(DASHBOARD_TOP_5_LIMIT)
    range_result = range_result.to_dict(orient="records")
    range_result = DashboardGlobalMeanDeviationSerailizer(range_result, many=True)

    range_result = range_result.data

    return range_result


# collection_name_dict = {
#     7: "one_week_mean",
#     30: "one_month_mean",
#     90: "three_month_mean",
#     180: "six_month_mean",
#     365: "one_year_mean",
# }

COLLECTION_NAME = "one_month_mean"


@method_decorator(cache_page(THIRTY_MINUTES_CACHE), name="dispatch")
class GlobalMeanDeviationAPIView(APIView):
    def get(self, request):
        price_changes = request.query_params.get("price_changes", PRICE_CHANGES_POS)

        mean_deviation_result = get_range_result(
            collection_name=COLLECTION_NAME, price_changes=price_changes
        )

        return Response(data=mean_deviation_result, status=status.HTTP_200_OK)
