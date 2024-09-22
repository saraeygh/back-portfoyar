from django.db.models import Sum
import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import (
    SIXTY_MINUTES_CACHE,
    ONE_YEAR_DATE_LIMIT,
    RIAL_TO_BILLION_TOMAN,
)
from domestic_market.models import DomesticCommodityType, DomesticTrade
from domestic_market.serializers import GetDomesticCommodityTypeSerailizer
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
class GetCommodityTypeListAPIView(APIView):
    def get(self, request, industry_id):
        commodity_types = list(
            DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
            .filter(commodity__commodity_type__industry_id=industry_id)
            .distinct("commodity__commodity_type")
            .values_list("commodity__commodity_type", flat=True)
        )

        commodity_types = DomesticCommodityType.objects.filter(
            id__in=commodity_types
        ).filter(industry_id=industry_id)
        commodity_type_df = GetDomesticCommodityTypeSerailizer(
            commodity_types, many=True
        )
        commodity_type_df = pd.DataFrame(commodity_type_df.data)

        yearly_value_df = []
        for commodity_type in commodity_types:
            yearly_value = (
                (
                    DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_DATE_LIMIT)
                    .filter(commodity__commodity_type__industry_id=industry_id)
                    .filter(commodity__commodity_type=commodity_type)
                    .aggregate(yearly_value=Sum("value", default=0))
                )["yearly_value"]
            ) / RIAL_TO_BILLION_TOMAN

            yearly_value_df.append(
                {"id": commodity_type.id, "year_value": yearly_value}
            )
        yearly_value_df = pd.DataFrame(yearly_value_df)

        commodity_type_df = pd.merge(commodity_type_df, yearly_value_df, on="id")

        if commodity_type_df.empty:
            return Response({}, status=status.HTTP_200_OK)

        commodity_type_df = commodity_type_df.sort_values(
            by="year_value", ascending=False
        )
        commodity_type_df["name"] = commodity_type_df.apply(add_value_to_name, axis=1)
        commodity_type_df = commodity_type_df.drop("year_value", axis=1)
        commodity_type_df = commodity_type_df.to_dict(orient="records")

        return Response(commodity_type_df, status=status.HTTP_200_OK)
