import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import SIXTY_SECONDS_CACHE, TOMAN_UNIT_IDENTIFIER

from domestic_market.models import DomesticDollarPrice
from domestic_market.serializers import GetDollarPriceSerializer


# @method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
class DollarPriceAPIView(APIView):
    def get(self, request):
        dollar_prices = DomesticDollarPrice.objects.all().order_by("-date")[0:60]

        dollar_prices = GetDollarPriceSerializer(dollar_prices, many=True)
        dollar_prices = pd.DataFrame(dollar_prices.data)
        dollar_prices["azad"] = dollar_prices["azad"] // 10
        dollar_prices["nima"] = dollar_prices["nima"] // 10
        dollar_prices.sort_values(by="date", ascending=True, inplace=True)
        dollar_prices.drop(["id", "date"], axis=1, inplace=True)

        dollar_prices.rename(
            columns={"date_shamsi": "x", "azad": "y_1", "nima": "y_2"}, inplace=True
        )

        chart = {
            "x_title": "تاریخ",
            "y_1_title": f"دلار آزاد ({TOMAN_UNIT_IDENTIFIER})",
            "y_2_title": f"دلار توافقی ({TOMAN_UNIT_IDENTIFIER})",
            "chart_title": "دلار",
            "history": dollar_prices.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
