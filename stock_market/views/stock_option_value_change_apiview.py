import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import STOCK_MONGO_DB, SIXTY_SECONDS_CACHE
from core.utils import (
    MongodbInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    SUMMARY_TABLE_COLS,
    add_index_as_id,
)

from stock_market.permissions import HasStockSubscription
from stock_market.serializers import (
    StockOptionValueChangeSerailizer,
    SummaryStockOptionValueChangeSerailizer,
)


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasStockSubscription])
class StockCallValueChangeAPIView(APIView):
    def get(self, request, option_type):

        if option_type == "call":
            collection_name = "call_value_change"
        elif option_type == "put":
            collection_name = "put_value_change"
        else:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name=collection_name
        )
        results = mongo_conn.collection.find({}, {"_id": 0})
        mongo_conn.client.close()

        results = pd.DataFrame(results)
        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results.sort_values(by="value_change", ascending=False)
        results.dropna(inplace=True)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        if table == ALL_TABLE_COLS:
            results = StockOptionValueChangeSerailizer(results, many=True)
        else:
            results = SummaryStockOptionValueChangeSerailizer(results, many=True)

        return Response(results.data, status=status.HTTP_200_OK)
