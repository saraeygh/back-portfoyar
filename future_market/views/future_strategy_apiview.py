import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from core.configs import SIX_HOURS_CACHE, SIXTY_SECONDS_CACHE

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from core.utils import set_json_cache, get_cache_as_json, RedisInterface
from future_market.tasks import FUTURE_STRATEGIES

redis_conn = RedisInterface(db=4)

RESULT_SORTING_COLUMN = "monthly_spread"


def sort_strategy_result(positions, sort_column):
    try:
        positions.sort_values(by=sort_column, inplace=True, ascending=False)
        return positions
    except KeyError:
        return positions


def get_strategy_result_from_redis(strategy_key):
    redis_conn = RedisInterface(db=4)
    positions = redis_conn.get_list_of_dicts(list_key=strategy_key)
    positions = pd.DataFrame(positions)
    positions = sort_strategy_result(positions, RESULT_SORTING_COLUMN)

    return positions


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@method_decorator(cache_page(SIX_HOURS_CACHE), name="dispatch")
class FuturePositionsAPIView(APIView):
    def get(self, request):
        future_strategy_list = list()
        for future_strategy_key, properties in FUTURE_STRATEGIES.items():
            future_strategy_list.append(
                {"name": properties["name"], "key": future_strategy_key}
            )

        return Response(future_strategy_list, status=status.HTTP_200_OK)

    def post(self, request):
        strategy_key = request.data.get("strategy_key")
        cache_key = f"FUTURE_POSITIONS_k_{strategy_key}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            result = get_strategy_result_from_redis(strategy_key)
            result = result.to_dict(orient="records")

            set_json_cache(cache_key, result, SIXTY_SECONDS_CACHE)
            return Response(result, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
