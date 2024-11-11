from datetime import datetime, timedelta
import pandas as pd

from django.db.models import Sum
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import SIXTY_MINUTES_CACHE, RIAL_TO_BILLION_TOMAN
from domestic_market.models import DomesticTrade
from domestic_market.utils import add_value_to_name


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetCommodityNameListByProducerAPIView(APIView):
    def get(self, request, company_id, group_id):
        ONE_YEAR_AGO = datetime.today().date() - timedelta(days=365)

        commodity_names = (
            DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_AGO)
            .filter(producer_id=company_id)
            .filter(commodity_id=group_id)
            .distinct("commodity_name")
            .values("id", "commodity_name")
        )
        commodity_names = pd.DataFrame(commodity_names)
        commodity_names = commodity_names.rename(columns={"commodity_name": "name"})

        commodity_name_list = commodity_names["name"].tolist()

        yearly_value_df = []
        for commodity_name in commodity_name_list:
            yearly_value = (
                (
                    DomesticTrade.objects.filter(trade_date__gt=ONE_YEAR_AGO)
                    .filter(producer_id=company_id)
                    .filter(commodity_id=group_id)
                    .filter(commodity_name=commodity_name)
                    .aggregate(yearly_value=Sum("value", default=0))
                )["yearly_value"]
            ) / RIAL_TO_BILLION_TOMAN

            yearly_value_df.append({"name": commodity_name, "year_value": yearly_value})
        yearly_value_df = pd.DataFrame(yearly_value_df)

        commodity_names = pd.merge(commodity_names, yearly_value_df, on="name")

        if commodity_names.empty:
            return Response({}, status=status.HTTP_200_OK)

        commodity_names = commodity_names.sort_values(by="year_value", ascending=False)
        commodity_names["name"] = commodity_names.apply(add_value_to_name, axis=1)
        commodity_names = commodity_names.drop("year_value", axis=1)
        commodity_names = commodity_names.to_dict(orient="records")

        return Response(commodity_names, status=status.HTTP_200_OK)
