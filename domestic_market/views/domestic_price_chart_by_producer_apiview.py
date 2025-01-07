from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import SIXTY_MINUTES_CACHE
from core.utils import set_json_cache, get_cache_as_json

from domestic_market.serializers import PriceChartSerailizer
from domestic_market.permissions import HasDomesticSubscription
from domestic_market.utils import get_price_chart_by_producer


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasDomesticSubscription])
class DomesticPriceChartByProducerAPIView(APIView):
    def post(self, request):
        producer_id = request.data.get("company_id")
        commodity_id = request.data.get("group_id")
        commodity_name_trade_id = request.data.get("commodity_id", None)

        if not isinstance(producer_id, int) or not isinstance(commodity_id, int):
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = (
            "DOMESTIC_PRICE_CHART_BY_PRODUCER"
            f"_p_{producer_id}"
            f"_c_{commodity_id}"
            f"_c_{commodity_name_trade_id}"
        )
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            price_chart = get_price_chart_by_producer(
                producer_id=producer_id,
                commodity_id=commodity_id,
                commodity_name_trade_id=commodity_name_trade_id,
            )
            if price_chart:
                price_chart_dic = PriceChartSerailizer(price_chart, many=True)

                set_json_cache(cache_key, price_chart_dic.data, SIXTY_MINUTES_CACHE)
                return Response(price_chart_dic.data, status=status.HTTP_200_OK)

            return Response(
                {"message": "هیچ تاریخچه‌ای پیدا نشد"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
