import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import STOCK_MONGO_DB, THIRTY_MINUTES_CACHE, DASHBOARD_TOP_5_LIMIT
from core.utils import MongodbInterface

from dashboard.serializers import MinimumPESerailizer


@method_decorator(cache_page(THIRTY_MINUTES_CACHE), name="dispatch")
class MinimumPEAPIView(APIView):
    def get(self, request):

        mongo_conn = MongodbInterface(db_name=STOCK_MONGO_DB, collection_name="roi")
        results = mongo_conn.collection.find({}, {"_id": 0})
        mongo_conn.client.close()

        results = pd.DataFrame(results)
        if results.empty:
            return Response([], status=status.HTTP_200_OK)
        results = results[
            (results["pe"] > 0) & (~results["symbol"].str.contains(r"\d"))
        ]

        results = results.sort_values(by="pe")
        results = results.head(DASHBOARD_TOP_5_LIMIT)
        results = results.to_dict(orient="records")
        results_srz = MinimumPESerailizer(results, many=True)

        return Response(results_srz.data, status=status.HTTP_200_OK)
