from django.db.models import Sum
import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import (
    SIXTY_MINUTES_CACHE,
    ONE_YEAR_DATE_LIMIT,
    RIAL_TO_BILLION_TOMAN,
)

from domestic_market.models import DomesticCommodity, DomesticTrade
from domestic_market.serializers import GetDomesticCommoditySerailizer
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
class GetCommodityListAPIView(APIView):
    def get(self, request, field_id):
        commodities = list(
            DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
            .filter(commodity__commodity_type_id=field_id)
            .distinct("commodity")
            .values_list("commodity", flat=True)
        )
        commodities = DomesticCommodity.objects.filter(id__in=commodities).filter(
            commodity_type_id=field_id
        )
        commodity_df = GetDomesticCommoditySerailizer(commodities, many=True)
        commodity_df = pd.DataFrame(commodity_df.data)

        yearly_value_df = []
        for commodity in commodities:
            yearly_value = (
                (
                    DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
                    .filter(commodity__commodity_type_id=field_id)
                    .filter(commodity=commodity)
                    .aggregate(yearly_value=Sum("value", default=0))
                )["yearly_value"]
            ) / RIAL_TO_BILLION_TOMAN

            yearly_value_df.append({"id": commodity.id, "year_value": yearly_value})
        yearly_value_df = pd.DataFrame(yearly_value_df)

        commodity_df = pd.merge(commodity_df, yearly_value_df, on="id")

        if commodity_df.empty:
            return Response({}, status=status.HTTP_200_OK)

        commodity_df = commodity_df.sort_values(by="year_value", ascending=False)
        commodity_df["name"] = commodity_df.apply(add_value_to_name, axis=1)
        commodity_df = commodity_df.drop("year_value", axis=1)
        commodity_df = commodity_df.to_dict(orient="records")

        return Response(commodity_df, status=status.HTTP_200_OK)
