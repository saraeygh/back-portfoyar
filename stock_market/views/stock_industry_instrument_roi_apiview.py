import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import STOCK_MONGO_DB, FIVE_MINUTES_CACHE, STOCK_NA_ROI
from core.utils import (
    MongodbInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    SUMMARY_TABLE_COLS,
    add_index_as_id,
)

from stock_market.serializers import MarketROISerailizer, SummaryMarketROISerailizer
from stock_market.utils import MAIN_PAPER_TYPE_DICT
from stock_market.permissions import HasStockSubscription


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasStockSubscription])
class StockIndustryInstrumentROIAPIView(APIView):
    def get(self, request, industry_id):

        mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="roi")
        results = mongo_conn.collection.find(
            {
                "industrial_group_id": industry_id,
                "paper_id": {"$in": list(MAIN_PAPER_TYPE_DICT.keys())},
            },
            {"_id": 0},
        )
        results = pd.DataFrame(results)

        results = results[(results["weekly_roi"] != STOCK_NA_ROI)]
        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results.sort_values(by="weekly_roi", ascending=False)
        results = results[~results["symbol"].str.contains(r"\d")]
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        if table == ALL_TABLE_COLS:
            results = MarketROISerailizer(results, many=True)
        else:
            results = SummaryMarketROISerailizer(results, many=True)

        return Response(results.data, status=status.HTTP_200_OK)
