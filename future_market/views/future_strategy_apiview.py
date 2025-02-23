import pandas as pd

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.configs import SIX_HOURS_CACHE, SIXTY_SECONDS_CACHE, FUTURE_REDIS_DB
from core.utils import (
    RedisInterface,
    TABLE_COLS_QP,
    ALL_TABLE_COLS,
    SUMMARY_TABLE_COLS,
    set_json_cache,
    get_cache_as_json,
    replace_arabic_letters_pd,
    add_index_as_id,
)

from future_market.tasks import FUTURE_STRATEGIES
from future_market.permissions import HasFutureSubscription


RESULT_SORTING_COLUMN = "monthly_spread"


LONG_SUMMARY_TABLE_LIST = [
    "derivative_name",
    "best_sell_price",
    "base_equity_name",
    "base_equity_last_price",
    "total_spread",
    "expiration_date",
    "monthly_spread",
    "initial_margin",
]
SHORT_SUMMARY_TABLE_LIST = [
    "derivative_name",
    "best_buy_price",
    "base_equity_name",
    "base_equity_last_price",
    "total_spread",
    "expiration_date",
    "monthly_spread",
    "initial_margin",
]


def sort_strategy_result(positions, sort_column, strategy_key, table):
    try:
        positions.sort_values(by=sort_column, inplace=True, ascending=False)

        positions["derivative_name"] = positions.apply(
            replace_arabic_letters_pd, args=("derivative_name",), axis=1
        )
        positions["base_equity_name"] = positions.apply(
            replace_arabic_letters_pd, args=("base_equity_name",), axis=1
        )

        if table == ALL_TABLE_COLS:
            pass
        else:
            if strategy_key == "long_future":
                positions = positions[LONG_SUMMARY_TABLE_LIST]
            else:
                positions = positions[SHORT_SUMMARY_TABLE_LIST]

        return positions
    except KeyError:
        return positions


def get_strategy_result_from_redis(strategy_key, table):
    redis_conn = RedisInterface(db=FUTURE_REDIS_DB)
    positions = redis_conn.get_list_of_dicts(list_key=strategy_key)
    positions = pd.DataFrame(positions)
    redis_conn.client.close()

    positions = sort_strategy_result(
        positions, RESULT_SORTING_COLUMN, strategy_key, table
    )

    return positions


@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class FuturePositionsAPIView(APIView):
    def get_authenticators(self):
        return [TokenAuthentication()]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasFutureSubscription()]

    def get(self, request):
        future_strategy_list = list()
        for future_strategy_key, properties in FUTURE_STRATEGIES.items():
            future_strategy_list.append(
                {"name": properties["name"], "key": future_strategy_key}
            )

        return Response(future_strategy_list, status=status.HTTP_200_OK)

    def post(self, request):
        strategy_key = request.data.get("strategy_key")

        table = request.query_params.get(TABLE_COLS_QP, SUMMARY_TABLE_COLS)
        cache_key = f"FUTURE_POSITIONS_k_{strategy_key}_{str(table)}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            result = get_strategy_result_from_redis(strategy_key, table)
            result.reset_index(drop=True, inplace=True)
            result["id"] = result.apply(add_index_as_id, axis=1)
            result = result.to_dict(orient="records")

            set_json_cache(cache_key, result, SIXTY_SECONDS_CACHE)
            return Response(result, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
