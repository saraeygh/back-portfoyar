from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_MINUTES_CACHE

from global_market.models import GlobalTrade
from global_market.serializers import GetGlobalTransitSerailizer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetTransitListAPIView(APIView):
    def get(self, request, commodity_id):
        global_transit = (
            GlobalTrade.objects.filter(commodity_id=commodity_id)
            .distinct("transit__transit_type")
            .order_by("transit__transit_type")
        )
        global_transit_srz = GetGlobalTransitSerailizer(global_transit, many=True)

        return Response(global_transit_srz.data, status=status.HTTP_200_OK)
