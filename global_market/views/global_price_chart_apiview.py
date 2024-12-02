from core.configs import SIXTY_MINUTES_CACHE
from core.utils import set_json_cache, get_cache_as_json
from global_market.serializers import PriceRatioChartSerailizer
from global_market.utils import get_price_chart
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GlobalPriceChartAPIView(APIView):
    def post(self, request):
        industry_id = request.data.get("industry_id")
        commodity_type_id = request.data.get("commodity_type_id")
        commodity_id = request.data.get("commodity_id")
        transit_id = request.data.get("transit_id")
        cache_key = (
            "GLOBAL_PRICE_CHART"
            f"_i_{industry_id}"
            f"_ct_{commodity_type_id}"
            f"_c_{commodity_id}"
            f"_t_{transit_id}"
        )

        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            price_chart_dict = get_price_chart(
                industry_id=industry_id,
                commodity_type_id=commodity_type_id,
                commodity_id=commodity_id,
                transit_id=transit_id,
            )

            if not price_chart_dict:
                return Response(
                    {"message": "مشکل در درخواست"}, status=status.HTTP_400_BAD_REQUEST
                )

            price_chart_dict_srz = PriceRatioChartSerailizer(
                price_chart_dict, many=True
            )

            # set_json_cache(cache_key, price_chart_dict_srz.data, SIXTY_MINUTES_CACHE)
            return Response(price_chart_dict_srz.data, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
