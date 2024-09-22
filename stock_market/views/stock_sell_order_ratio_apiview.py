from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import pandas as pd
from core.configs import STOCK_DB, SIXTY_SECONDS_CACHE, STOCK_TOP_500_LIMIT

from core.utils import MongodbInterface, add_index_as_id
from stock_market.serializers import SellOrderRatioSerailizer
from stock_market.utils import MAIN_PAPER_TYPE_DICT

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class StockSellOrderRatioAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(db_name=STOCK_DB, collection_name="sell_ratio")
        results = mongo_client.collection.find(
            {"paper_type": {"$in": list(MAIN_PAPER_TYPE_DICT.keys())}}, {"_id": 0}
        )
        results = pd.DataFrame(results)

        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results[~results["symbol"].str.contains(r"\d")]
        results = results.sort_values(by="sell_ratio", ascending=False)
        results = results.head(STOCK_TOP_500_LIMIT)
        results.reset_index(drop=True, inplace=True)
        results["id"] = results.apply(add_index_as_id, axis=1)
        results = results.to_dict(orient="records")

        results = SellOrderRatioSerailizer(results, many=True)

        return Response(results.data, status=status.HTTP_200_OK)
