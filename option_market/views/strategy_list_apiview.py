from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIX_HOURS_CACHE

from option_market.models import OptionStrategy
from option_market.serializers import StrategyListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class StrategyListAPIView(APIView):
    def get(self, request):
        strategy_list = OptionStrategy.objects.all().order_by("name")
        strategy_list = StrategyListSerializer(strategy_list, many=True)

        return Response(strategy_list.data, status=status.HTTP_200_OK)


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class FilteredStrategyListAPIView(APIView):
    def get(self, request, risk_level):
        strategy_list = OptionStrategy.objects.filter(
            risk_level__level=risk_level
        ).order_by("name")
        if not strategy_list.exists():
            strategy_list = OptionStrategy.objects.all().order_by("name")
        strategy_list = StrategyListSerializer(strategy_list, many=True)

        return Response(strategy_list.data, status=status.HTTP_200_OK)
