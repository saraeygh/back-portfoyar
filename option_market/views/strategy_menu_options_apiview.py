from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIX_HOURS_CACHE

from option_market.models import RiskLevel, StrategyOption
from option_market.serializers import RiskLevelListSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class ProfitStatusesAPIView(APIView):
    def get(self, request):

        profit_status_list = [
            {"name": "همه", "key": "all_profit"},
        ]

        for profit_status in StrategyOption.PROFIT_STATUS_CHOICES:
            profit_status_list.append(
                {"name": profit_status[1], "key": profit_status[0]}
            )

        return Response(profit_status_list, status=status.HTTP_200_OK)


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class StrategiesAPIView(APIView):
    def get(self, request, risk_level, profit_status):
        if profit_status == "all_profit":
            strategy_list = list(
                StrategyOption.objects.filter(risk_level=risk_level).values(
                    "name", "key"
                )
            )
        else:
            strategy_list = list(
                StrategyOption.objects.filter(
                    risk_level=risk_level, profit_status=profit_status
                ).values("name", "key")
            )

        return Response(strategy_list, status=status.HTTP_200_OK)


################################## OLD #################################
@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class ProfitStatusListAPIView(APIView):
    def get(self, request):

        profit_status_list = [
            {"name": "همه", "key": "all_profit"},
        ]

        for profit_status in RiskLevel.PROFIT_STATUS_CHOICES:
            profit_status_list.append(
                {"name": profit_status[1], "key": profit_status[0]}
            )

        return Response(profit_status_list, status=status.HTTP_200_OK)


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class RiskLevelListAPIView(APIView):
    def get(self, request, profit_status):

        if profit_status == "all_profit":
            risk_level_list = RiskLevel.objects.distinct("level")
            risk_level_list = RiskLevelListSerializer(risk_level_list, many=True)
        else:
            risk_level_list = RiskLevel.objects.filter(
                profit_status=profit_status
            ).distinct("level")
            risk_level_list = RiskLevelListSerializer(risk_level_list, many=True)

        risk_level_list = list(risk_level_list.data)
        risk_level_list.insert(0, {"name": "همه", "key": "all_risk"})

        return Response(risk_level_list, status=status.HTTP_200_OK)
