import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.utils import MongodbInterface
from core.configs import SIXTY_MINUTES_CACHE, DOMESTIC_MONGO_DB


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetProducerListAPIView(APIView):
    def get(self, request):
        mongo_client = MongodbInterface(
            db_name=DOMESTIC_MONGO_DB, collection_name="producers_yearly_value"
        )
        producers = list(mongo_client.collection.find({}, {"_id": 0}))
        producers = pd.DataFrame(producers)
        if producers.empty:
            return Response({}, status=status.HTTP_200_OK)

        producers = producers.sort_values(by="year_value", ascending=False)
        producers = producers.drop("year_value", axis=1)
        producers = producers.to_dict(orient="records")

        return Response(producers, status=status.HTTP_200_OK)
