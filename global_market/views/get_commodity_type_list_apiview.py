from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_MINUTES_CACHE

from global_market.models import GlobalCommodityType
from global_market.serializers import GetGlobalCommodityTypeSerailizer
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
        global_commodity_type = GlobalCommodityType.objects.filter(
            industry_id=industry_id
        ).order_by("name")
        global_commodity_type_srz = GetGlobalCommodityTypeSerailizer(
            global_commodity_type, many=True
        )

        return Response(global_commodity_type_srz.data, status=status.HTTP_200_OK)
