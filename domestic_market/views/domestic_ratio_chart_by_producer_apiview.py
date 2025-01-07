from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes

from core.configs import SIXTY_MINUTES_CACHE
from core.utils import set_json_cache, get_cache_as_json

from domestic_market.serializers import RatioChartSerailizer
from domestic_market.permissions import HasDomesticSubscription
from domestic_market.utils import get_price_chart_by_producer, get_ratio_chart


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, HasDomesticSubscription])
class DomesticRatioChartByProducerAPIView(APIView):
    def post(self, request):
        producer_id_1 = request.data.get("company1_id")
        commodity_id_1 = request.data.get("group1_id")
        commodity_name_trade_id_1 = request.data.get("commodity1_id", None)

        producer_id_2 = request.data.get("company2_id")
        commodity_id_2 = request.data.get("group2_id")
        commodity_name_trade_id_2 = request.data.get("commodity2_id", None)

        if (
            not isinstance(producer_id_1, int)
            or not isinstance(commodity_id_1, int)
            or not isinstance(producer_id_2, int)
            or not isinstance(commodity_id_2, int)
        ):
            return Response(
                {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = (
            "DOMESTIC_RATIO_CHART"
            f"_p1_{producer_id_1}"
            f"_c1_{commodity_id_1}"
            f"_cn1_{commodity_name_trade_id_1}"
            f"_p2_{producer_id_2}"
            f"_c2_{commodity_id_2}"
            f"_cn2_{commodity_name_trade_id_2}"
        )
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            try:
                plt_1 = get_price_chart_by_producer(
                    producer_id=producer_id_1,
                    commodity_id=commodity_id_1,
                    commodity_name_trade_id=commodity_name_trade_id_1,
                )

                plt_2 = get_price_chart_by_producer(
                    producer_id=producer_id_2,
                    commodity_id=commodity_id_2,
                    commodity_name_trade_id=commodity_name_trade_id_2,
                )
            except ValueError:
                return Response(
                    {"message": "هیچ تاریخچه‌ای پیدا نشد"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ratio_list = get_ratio_chart(plt_1, plt_2)
            ratio_list_srz = RatioChartSerailizer(ratio_list, many=True)

            set_json_cache(cache_key, ratio_list_srz.data, SIXTY_MINUTES_CACHE)
            return Response(ratio_list_srz.data, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
