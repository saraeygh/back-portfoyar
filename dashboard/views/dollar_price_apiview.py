import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.configs import FIVE_MINUTES_CACHE

from domestic_market.models import DomesticDollarPrice
from domestic_market.serializers import GetDollarPriceSerializer


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
class DollarPriceAPIView(APIView):
    def get(self, request):
        dollar_prices = DomesticDollarPrice.objects.all().order_by("date")[0:365]

        dollar_prices = GetDollarPriceSerializer(dollar_prices, many=True)
        dollar_prices = pd.DataFrame(dollar_prices.data)

        dollar_prices.drop(["id", "date"], axis=1, inplace=True)

        dollar_prices.rename(
            columns={"date_shamsi": "x", "azad": "y_1", "nima": "y_2"}, inplace=True
        )

        chart = {
            "x_title": "تاریخ",
            "y_1_title": "دلار آزاد",
            "y_2_title": "دلار نیما",
            "chart_title": "تغییرات قیمت دلار در یکسال گذشته",
            "history": dollar_prices.to_dict(orient="records"),
        }

        return Response(chart, status=status.HTTP_200_OK)
