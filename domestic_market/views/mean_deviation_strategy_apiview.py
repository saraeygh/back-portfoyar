import pandas as pd

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import SIX_HOURS_CACHE, DOMESTIC_MONGO_DB, COMMODITY_TOP_200_LIMIT
from core.utils import (
    MongodbInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    SUMMARY_TABLE_COLS,
    set_json_cache,
    get_cache_as_json,
    add_index_as_id,
)

from domestic_market.permissions import HasDomesticSubscription
from domestic_market.serializers import (
    DomesticMeanDeviationSerailizer,
    SummaryDomesticMeanDeviationSerailizer,
)

POSITIVE_RANGE = "positive_range"
NEGATIVE_RANGE = "negative_range"


def get_range_result(collection_name, range_name, table=None):
    mongo_conn = MongodbInterface(
        db_name=DOMESTIC_MONGO_DB, collection_name=collection_name
    )
    if range_name == POSITIVE_RANGE:
        range_result = list(
            mongo_conn.collection.find({"deviation": {"$gte": 0}}, {"_id": 0})
        )
    else:
        range_result = list(
            mongo_conn.collection.find({"deviation": {"$lt": 0}}, {"_id": 0})
        )

    range_result = pd.DataFrame(range_result)
    if range_result.empty:
        range_result = []
        return range_result

    if range_name == POSITIVE_RANGE:
        range_result = range_result.sort_values(by="deviation", ascending=False)
    else:
        range_result = range_result.sort_values(by="deviation", ascending=True)

    range_result = range_result.head(COMMODITY_TOP_200_LIMIT)
    range_result.reset_index(drop=True, inplace=True)
    range_result["id"] = range_result.apply(add_index_as_id, axis=1)
    range_result = range_result.to_dict(orient="records")

    if table == ALL_TABLE_COLS:
        range_result = DomesticMeanDeviationSerailizer(range_result, many=True)
    else:
        range_result = SummaryDomesticMeanDeviationSerailizer(range_result, many=True)

    range_result = range_result.data

    return range_result


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasDomesticSubscription])
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

        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        cache_key = f"DOMESTIC_MEAN_DEVIATION_duration_{duration}_{str(table)}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            collection_name = collection_name_dict.get(duration)
            mean_deviation_result = {}

            mean_deviation_result[POSITIVE_RANGE] = get_range_result(
                collection_name=collection_name,
                range_name=POSITIVE_RANGE,
                table=table,
            )
            mean_deviation_result[NEGATIVE_RANGE] = get_range_result(
                collection_name=collection_name,
                range_name=NEGATIVE_RANGE,
                table=table,
            )

            set_json_cache(cache_key, mean_deviation_result, SIX_HOURS_CACHE)
            return Response(data=mean_deviation_result, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)


##############################################################################


PRICE_CHANGES_POS = "inc"
PRICE_CHANGES_NEG = "dec"


def get_range_result_v2(collection_name, price_changes, table=None):
    mongo_conn = MongodbInterface(
        db_name=DOMESTIC_MONGO_DB, collection_name=collection_name
    )
    if price_changes == PRICE_CHANGES_POS:
        range_result = list(
            mongo_conn.collection.find({"deviation": {"$gte": 0}}, {"_id": 0})
        )
    else:
        range_result = list(
            mongo_conn.collection.find({"deviation": {"$lt": 0}}, {"_id": 0})
        )

    range_result = pd.DataFrame(range_result)
    if range_result.empty:
        range_result = []
        return range_result

    if price_changes == PRICE_CHANGES_POS:
        range_result = range_result.sort_values(by="deviation", ascending=False)
    else:
        range_result = range_result.sort_values(by="deviation", ascending=True)

    range_result = range_result.head(COMMODITY_TOP_200_LIMIT)
    range_result.reset_index(drop=True, inplace=True)
    range_result["id"] = range_result.apply(add_index_as_id, axis=1)
    range_result = range_result.to_dict(orient="records")

    if table == ALL_TABLE_COLS:
        range_result = DomesticMeanDeviationSerailizer(range_result, many=True)
    else:
        range_result = SummaryDomesticMeanDeviationSerailizer(range_result, many=True)

    range_result = range_result.data

    return range_result


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasDomesticSubscription])
class MeanDeviationAPIViewV2(APIView):
    def get(self, request):
        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        duration = int(request.query_params.get("duration", 7))
        price_changes = request.query_params.get("price_changes", PRICE_CHANGES_POS)

        collection_name_dict = {
            7: "one_week_mean",
            30: "one_month_mean",
            90: "three_month_mean",
            180: "six_month_mean",
            365: "one_year_mean",
        }

        cache_key = f"DOMESTIC_MEAN_DEVIATION_{duration}_{price_changes}_{str(table)}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            collection_name = collection_name_dict.get(duration)

            mean_deviation_result = get_range_result_v2(
                collection_name=collection_name,
                price_changes=price_changes,
                table=table,
            )

            set_json_cache(cache_key, mean_deviation_result, SIX_HOURS_CACHE)
            return Response(data=mean_deviation_result, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
