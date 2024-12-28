import pandas as pd

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import STOCK_MONGO_DB
from core.utils import MongodbInterface, ALL_TABLE_COLS, TABLE_COLS_QP, add_index_as_id

from stock_market.serializers import (
    StockOptionPriceSpreadSerailizer,
    SummaryStockOptionPriceSpreadSerailizer,
)

from option_market.permissions import HasOptionSubscription


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasOptionSubscription])
class PriceSpreadStrategyAPIView(APIView):
    def post(self, request):

        mongo_client = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="option_price_spread"
        )
        results = mongo_client.collection.find({}, {"_id": 0})

        strike_deviation = int(request.data.get("strike_deviation"))
        results = pd.DataFrame(results)
        results = results[abs(results["strike_deviation"]) <= strike_deviation]

        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results.sort_values(by="price_spread", ascending=False)
        results.dropna(inplace=True)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        table = request.query_params.get(TABLE_COLS_QP)
        if table and table == ALL_TABLE_COLS:
            results = StockOptionPriceSpreadSerailizer(results, many=True)
        else:
            results = SummaryStockOptionPriceSpreadSerailizer(results, many=True)

        return Response(results.data, status=status.HTTP_200_OK)
