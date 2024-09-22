from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from core.configs import THIRTY_MINUTES_CACHE, DOMESTIC_DB

from core.utils import MongodbInterface
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(THIRTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class ProducerSellReportAPIView(APIView):
    def get(self, request, company_id):

        mongo_client = MongodbInterface(
            db_name=DOMESTIC_DB, collection_name="producer_sell"
        )

        producer_sell_report = list(
            mongo_client.collection.find({"producer_id": company_id}, {"_id": 0})
        )

        if producer_sell_report:
            producer_sell_report = producer_sell_report[0]["report"]
            return Response(data=producer_sell_report, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"detain": "No resutl"}, status=status.HTTP_400_BAD_REQUEST
            )
