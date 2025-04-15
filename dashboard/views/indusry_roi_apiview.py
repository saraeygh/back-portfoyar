import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import MongodbInterface
from core.configs import STOCK_MONGO_DB, THIRTY_MINUTES_CACHE, DASHBOARD_TOP_5_LIMIT

from stock_market.serializers import DashboardIndustryROISerailizer


# @method_decorator(cache_page(THIRTY_MINUTES_CACHE), name="dispatch")
class IndustryROIAPIView(APIView):
    def get(self, request):

        mongo_conn = MongodbInterface(
            db_name=STOCK_MONGO_DB, collection_name="industry_ROI"
        )
        results = list(mongo_conn.collection.find({}, {"_id": 0}))

        results = pd.DataFrame(results)
        if results.empty:
            return Response([], status=status.HTTP_200_OK)

        results = results.sort_values(by="half_yearly_roi", ascending=False)
        results = results.head(DASHBOARD_TOP_5_LIMIT)
        results = results.to_dict(orient="records")
        results_srz = DashboardIndustryROISerailizer(results, many=True)

        return Response(results_srz.data, status=status.HTTP_200_OK)
