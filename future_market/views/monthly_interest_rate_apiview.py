from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIX_HOURS_CACHE
from core.models import FeatureToggle
from core.utils import MONTHLY_INTEREST_RATE_NAME

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class MonthlyInterestRateAPIView(APIView):
    def get(self, request):
        monthly_interest_rate = FeatureToggle.objects.get(
            name=MONTHLY_INTEREST_RATE_NAME
        )
        monthly_interest_rate = float(monthly_interest_rate.value)

        return Response(
            {"monthly_interest_rate": monthly_interest_rate}, status=status.HTTP_200_OK
        )
