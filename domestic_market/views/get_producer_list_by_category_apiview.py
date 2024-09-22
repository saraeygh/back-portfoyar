from django.db.models import Sum
import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_MINUTES_CACHE, ONE_YEAR_DATE_LIMIT, RIAL_TO_BILLION_TOMAN

from domestic_market.models import DomesticTrade
from domestic_market.serializers import GetDomesticProducerSerailizer
from domestic_market.utils import add_value_to_name
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetProducerListByCommodityAPIView(APIView):
    def get(self, request, group_id):
        producers = list(
            DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
            .filter(commodity_id=group_id)
            .distinct("producer")
        )
        producers = GetDomesticProducerSerailizer(producers, many=True)
        producer_df = pd.DataFrame(producers.data)

        producer_id_list = [producer["id"] for producer in producers.data]
        yearly_value_df = []
        for producer_id in producer_id_list:
            yearly_value = (
                (
                    DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
                    .filter(producer_id=producer_id)
                    .aggregate(yearly_value=Sum("value", default=0))
                )["yearly_value"]
            ) / RIAL_TO_BILLION_TOMAN

            yearly_value_df.append({"id": producer_id, "year_value": yearly_value})
        yearly_value_df = pd.DataFrame(yearly_value_df)

        producer_df = pd.merge(producer_df, yearly_value_df, on="id")

        if producer_df.empty:
            return Response({}, status=status.HTTP_200_OK)

        producer_df = producer_df.sort_values(by="year_value", ascending=False)
        producer_df["name"] = producer_df.apply(add_value_to_name, axis=1)
        producer_df = producer_df.drop("year_value", axis=1)
        producer_df = producer_df.to_dict(orient="records")

        return Response(producer_df, status=status.HTTP_200_OK)
