from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import pandas as pd
from core.configs import STOCK_MONGO_DB, FIVE_MINUTES_CACHE

from core.utils import MongodbInterface, add_index_as_id
from stock_market.serializers import StockOptionPriceSpreadSerailizer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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
        results_srz = StockOptionPriceSpreadSerailizer(results, many=True)

        return Response(results_srz.data, status=status.HTTP_200_OK)
