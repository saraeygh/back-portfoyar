from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIX_HOURS_CACHE

from option_market.models import Strategy
from option_market.serializers import StrategySerializer
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class StrategyAPIView(APIView):
    def get(self, request):
        strategies = Strategy.objects.all().order_by("name")
        strategies_srz = StrategySerializer(strategies, many=True)

        return Response(strategies_srz.data)
