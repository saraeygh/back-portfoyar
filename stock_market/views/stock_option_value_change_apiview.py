from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import pandas as pd
from core.configs import STOCK_DB, SIXTY_SECONDS_CACHE, RIAL_TO_MILLION_TOMAN

from core.utils import MongodbInterface, add_index_as_id
from stock_market.serializers import StockOptionValueChangeSerailizer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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

        mongo_client = MongodbInterface(
            db_name=STOCK_DB, collection_name=collection_name
        )
        results = mongo_client.collection.find({}, {"_id": 0})

        results = pd.DataFrame(results)

        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results.sort_values(by="value_change", ascending=False)
        results.dropna(inplace=True)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results["last_mean"] = results["last_mean"]
        results["month_mean"] = results["month_mean"]
        results = results.to_dict(orient="records")
        results_srz = StockOptionValueChangeSerailizer(results, many=True)

        return Response(results_srz.data, status=status.HTTP_200_OK)
