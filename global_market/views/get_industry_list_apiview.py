from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIXTY_MINUTES_CACHE

from global_market.models import GlobalIndustry
from global_market.serializers import GetGlobalIndustrySerailizer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIXTY_MINUTES_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class GetIndustryListAPIView(APIView):
    def get(self, request):
        global_industry = GlobalIndustry.objects.all().order_by("name")
        global_industry_srz = GetGlobalIndustrySerailizer(global_industry, many=True)

        return Response(global_industry_srz.data, status=status.HTTP_200_OK)
