import pandas as pd
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import SIX_HOURS_CACHE, DOMESTIC_MONGO_DB, COMMODITY_TOP_200_LIMIT
from core.utils import (
    MongodbInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    set_json_cache,
    get_cache_as_json,
    add_index_as_id,
)

from domestic_market.serializers import (
    DomesticMeanDeviationSerailizer,
    SummaryDomesticMeanDeviationSerailizer,
)


def get_range_result(collection_name, range_name, table=None):
    mongo_client = MongodbInterface(
        db_name=DOMESTIC_MONGO_DB, collection_name=collection_name
    )

    if range_name == "positive_range":
        range_result = list(
            mongo_client.collection.find({"deviation": {"$gte": 0}}, {"_id": 0})
        )
    else:
        range_result = list(
            mongo_client.collection.find({"deviation": {"$lt": 0}}, {"_id": 0})
        )

    range_result = pd.DataFrame(range_result)
    if range_result.empty:
        range_result = []
        return range_result

    if range_name == "positive_range":
        range_result = range_result.sort_values(by="deviation", ascending=False)
    else:
        range_result = range_result.sort_values(by="deviation", ascending=True)

    range_result = range_result.head(COMMODITY_TOP_200_LIMIT)
    range_result.reset_index(drop=True, inplace=True)
    range_result["id"] = range_result.apply(add_index_as_id, axis=1)
    range_result = range_result.to_dict(orient="records")

    if table and table == ALL_TABLE_COLS:
        range_result = DomesticMeanDeviationSerailizer(range_result, many=True)
    else:
        range_result = SummaryDomesticMeanDeviationSerailizer(range_result, many=True)

    range_result = range_result.data

    return range_result


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class MeanDeviationAPIView(APIView):
    def post(self, request):
        duration = request.data.get("duration")
        collection_name_dict = {
            7: "one_week_mean",
            30: "one_month_mean",
            90: "three_month_mean",
            180: "six_month_mean",
            365: "one_year_mean",
        }

        table = request.query_params.get(TABLE_COLS_QP)
        cache_key = f"DOMESTIC_MEAN_DEVIATION_duration_{duration}_{str(table)}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            collection_name = collection_name_dict.get(duration)
            mean_deviation_result = {}

            mean_deviation_result["positive_range"] = get_range_result(
                collection_name=collection_name,
                range_name="positive_range",
                table=table,
            )
            mean_deviation_result["negative_range"] = get_range_result(
                collection_name=collection_name,
                range_name="negative_range",
                table=table,
            )

            set_json_cache(cache_key, mean_deviation_result, SIX_HOURS_CACHE)
            return Response(data=mean_deviation_result, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
