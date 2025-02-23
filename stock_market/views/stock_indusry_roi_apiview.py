import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import STOCK_MONGO_DB, THIRTY_MINUTES_CACHE
from core.utils import MongodbInterface

from stock_market.serializers import IndustryROISerailizer
from stock_market.permissions import HasStockSubscription


@method_decorator(cache_page(THIRTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasStockSubscription])
class StockIndustryROIAPIView(APIView):
    def get(self, request):

        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="industry_ROI"
        )
        results = mongo_conn.collection.find({}, {"_id": 0})
        results = pd.DataFrame(results)
        mongo_conn.client.close()
        if results.empty:
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        results = results.sort_values(by="industrial_group_name")
        results = results.to_dict(orient="records")
        results_srz = IndustryROISerailizer(results, many=True)

        return Response(results_srz.data, status=status.HTTP_200_OK)
