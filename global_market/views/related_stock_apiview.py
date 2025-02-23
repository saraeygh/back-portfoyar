import pandas as pd

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import THIRTY_MINUTES_CACHE, STOCK_MONGO_DB
from core.utils import (
    MongodbInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    SUMMARY_TABLE_COLS,
    set_json_cache,
    get_cache_as_json,
)

from stock_market.serializers import MarketROISerailizer, SummaryMarketROISerailizer

from global_market.serializers import GlobalRelatedStockSerailizer
from global_market.models import GlobalCommodityType, GlobalRelation
from global_market.permissions import HasGlobalSubscription


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasGlobalSubscription])
class RelatedStockAPIView(APIView):
    def post(self, request):
        commodity_type = request.data.get("commodity_type")
        commodity_type = get_object_or_404(GlobalCommodityType, name=commodity_type)

        cache_key = f"GLOBAL_RELATED_STOCK_{commodity_type.id}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            related_stock = GlobalRelation.objects.filter(
                global_commodity_type=commodity_type
            )
            related_stock = GlobalRelatedStockSerailizer(related_stock, many=True)
            related_stock = pd.DataFrame(related_stock.data)

            mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="roi")
            stock_info = mongo_conn.collection.find({}, {"_id": 0})
            stock_info = pd.DataFrame(stock_info)
            mongo_conn.client.close()

            if related_stock.empty or stock_info.empty:
                return Response(data=[], status=status.HTTP_200_OK)

            related_stock = related_stock.merge(stock_info, on="ins_code", how="left")
            related_stock = related_stock.drop(
                [
                    "ins_code",
                    "market_id",
                    "market_name",
                    "paper_id",
                    "paper_name",
                    "industrial_group_id",
                    "industrial_group_name",
                ],
                axis=1,
            )

            related_stock.dropna(inplace=True)
            related_stock = related_stock.to_dict(orient="records")

            table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
            if table == ALL_TABLE_COLS:
                related_stock = MarketROISerailizer(related_stock, many=True)
            else:
                related_stock = SummaryMarketROISerailizer(related_stock, many=True)

            set_json_cache(cache_key, related_stock.data, THIRTY_MINUTES_CACHE)
            return Response(related_stock.data, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
