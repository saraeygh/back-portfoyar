from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import FIVE_MINUTES_CACHE

from domestic_market.models import DomesticDollarPrice
from domestic_market.serializers import GetDollarPriceSerializer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(FIVE_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetDollarPriceAPIView(APIView):
    def get(self, request):
        try:
            records = int(request.query_params.get("records"))
            dollar_prices = DomesticDollarPrice.objects.all().order_by("-date")[
                0:records
            ]
        except Exception:
            dollar_prices = DomesticDollarPrice.objects.all().order_by("-date")

        dollar_prices_srz = GetDollarPriceSerializer(dollar_prices, many=True)

        return Response(dollar_prices_srz.data, status=status.HTTP_200_OK)
