from datetime import datetime, timedelta
import pandas as pd

from django.db.models import Sum
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from core.configs import SIXTY_MINUTES_CACHE, RIAL_TO_BILLION_TOMAN

from domestic_market.models import DomesticIndustry, DomesticTrade
from domestic_market.serializers import GetDomesticIndustrySerailizer
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
class GetIndustryListAPIView(APIView):
    def get(self, request):
        ONE_YEAR_AGO = datetime.today().date() - timedelta(days=365)
        industries = list(
            DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_AGO)
            .distinct("commodity__commodity_type__industry")
            .values_list("commodity__commodity_type__industry", flat=True)
        )

        industries = DomesticIndustry.objects.filter(id__in=industries)
        industry_df = GetDomesticIndustrySerailizer(industries, many=True)
        industry_df = pd.DataFrame(industry_df.data)

        yearly_value_df = []
        for industry in industries:
            yearly_value = (
                (
                    DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_AGO)
                    .filter(commodity__commodity_type__industry=industry)
                    .aggregate(yearly_value=Sum("value", default=0))
                )["yearly_value"]
            ) / RIAL_TO_BILLION_TOMAN

            yearly_value_df.append({"id": industry.id, "year_value": yearly_value})
        yearly_value_df = pd.DataFrame(yearly_value_df)

        industry_df = pd.merge(industry_df, yearly_value_df, on="id")

        if industry_df.empty:
            return Response({}, status=status.HTTP_200_OK)

        industry_df = industry_df.sort_values(by="year_value", ascending=False)
        industry_df["name"] = industry_df.apply(add_value_to_name, axis=1)
        industry_df = industry_df.drop("year_value", axis=1)
        industry_df = industry_df.to_dict(orient="records")

        return Response(industry_df, status=status.HTTP_200_OK)
