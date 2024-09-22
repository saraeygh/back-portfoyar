from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_MINUTES_CACHE

from global_market.models import GlobalCommodity
from global_market.serializers import GetGlobalCommoditySerailizer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetCommodityListAPIView(APIView):
    def get(self, request, commodity_type_id):
        global_commodity = GlobalCommodity.objects.filter(
            commodity_type_id=commodity_type_id
        ).order_by("name")
        global_commodity_srz = GetGlobalCommoditySerailizer(global_commodity, many=True)

        return Response(global_commodity_srz.data, status=status.HTTP_200_OK)
