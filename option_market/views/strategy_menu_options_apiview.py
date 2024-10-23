import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIX_HOURS_CACHE

from option_market.models import StrategyOption
from option_market.models.strategy_option_model import PROFIT_STATUS_CHOICES
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class ProfitStatusesAPIView(APIView):
    def get(self, request):

        profit_status_list = [
            {"name": "همه", "key": "all_profit"},
        ]

        for profit_status in PROFIT_STATUS_CHOICES:
            profit_status_list.append(
                {"name": profit_status[1], "key": profit_status[0]}
            )

        return Response(profit_status_list, status=status.HTTP_200_OK)


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class StrategiesAPIView(APIView):
    def get(self, request, risk_level, profit_status):
        if profit_status == "all_profit" and risk_level == "all_risk":
            strategy_list = list(
                StrategyOption.objects.all()
                .distinct("key")
                .values("name", "key", "sequence")
            )
        elif profit_status == "all_profit":
            strategy_list = list(
                StrategyOption.objects.filter(risk_level=risk_level).values(
                    "name", "key", "sequence"
                )
            )
        else:
            strategy_list = list(
                StrategyOption.objects.filter(
                    risk_level=risk_level, profit_status=profit_status
                ).values("name", "key", "sequence")
            )

        if strategy_list:
            strategy_list = pd.DataFrame(strategy_list)
            strategy_list.sort_values(by="sequence", inplace=True)
            strategy_list.drop(columns=["sequence"], inplace=True)
            strategy_list = strategy_list.to_dict(orient="records")

        return Response(strategy_list, status=status.HTTP_200_OK)
