from django.db.models import Sum
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import pandas as pd

from core.configs import SIXTY_MINUTES_CACHE, ONE_YEAR_DATE_LIMIT, RIAL_TO_BILLION_TOMAN
from domestic_market.models import DomesticTrade
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
class GetCommodityListByProducerAPIView(APIView):
    def get(self, request, company_id):

        commodity_df = (
            DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
            .filter(producer_id=company_id)
            .distinct("commodity")
            .values("commodity", "commodity__name")
        )
        commodity_df = pd.DataFrame(commodity_df)
        commodity_df = commodity_df.rename(
            columns={"commodity": "id", "commodity__name": "name"}
        )

        commodity_id_list = commodity_df["id"].tolist()
        yearly_value_df = []
        for commodity_id in commodity_id_list:
            yearly_value = (
                (
                    DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
                    .filter(producer_id=company_id)
                    .filter(commodity_id=commodity_id)
                    .aggregate(yearly_value=Sum("value", default=0))
                )["yearly_value"]
            ) / RIAL_TO_BILLION_TOMAN

            yearly_value_df.append({"id": commodity_id, "year_value": yearly_value})
        yearly_value_df = pd.DataFrame(yearly_value_df)

        commodity_df = pd.merge(commodity_df, yearly_value_df, on="id")

        if commodity_df.empty:
            return Response({}, status=status.HTTP_200_OK)

        commodity_df = commodity_df.sort_values(by="year_value", ascending=False)
        commodity_df["name"] = commodity_df.apply(add_value_to_name, axis=1)
        commodity_df = commodity_df.drop("year_value", axis=1)
        commodity_df = commodity_df.to_dict(orient="records")

        return Response(commodity_df, status=status.HTTP_200_OK)
