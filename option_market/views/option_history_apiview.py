import pandas as pd
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from core.configs import (
    SIXTY_SECONDS_CACHE,
    SIXTY_MINUTES_CACHE,
    OPTION_DB,
    OPTION_REDIS_DB,
)
from core.utils import (
    RedisInterface,
    MongodbInterface,
    set_json_cache,
    get_cache_as_json,
)

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from option_market.serializers import SymbolHistorySerializer

redis_conn = RedisInterface(db=OPTION_REDIS_DB)


@method_decorator(cache_page(SIXTY_SECONDS_CACHE), name="dispatch")
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class OptionAssetNamesAPIView(APIView):
    def get(self, request):

        option_base_equity = pd.DataFrame(
            redis_conn.get_list_of_dicts(list_key="option_data")
        )
        option_base_equity.sort_values(by="base_equity_symbol", inplace=True)
        option_base_equity = option_base_equity["base_equity_symbol"].unique().tolist()

        return Response(option_base_equity)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class AssetOptionSymbolsAPIView(APIView):
    def post(self, request):
        asset_name = request.data.get("asset_name")
        cache_key = f"OPTIONS_ASSET_SYMBOLS_a_{asset_name}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            asset_options_list = pd.DataFrame(
                redis_conn.get_list_of_dicts(list_key="option_data")
            )
            asset_options_list = asset_options_list[
                asset_options_list["base_equity_symbol"] == asset_name
            ]
            asset_options_list = (
                asset_options_list["call_symbol"].to_list()
                + asset_options_list["put_symbol"].to_list()
            )
            asset_options_list = sorted(asset_options_list)
            set_json_cache(cache_key, asset_options_list, SIXTY_SECONDS_CACHE)
            return Response(asset_options_list, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class SymbolHistoryAPIView(APIView):
    def post(self, request):
        symbol = request.data.get("symbol")
        cache_key = f"OPTIONS_SYMBOL_HISTORY_s_{symbol}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            mongodb_conn = MongodbInterface(
                db_name=OPTION_DB, collection_name="history"
            )

            query_filter = {"option_symbol": symbol}
            symbol_history = mongodb_conn.collection.find_one(query_filter, {"_id": 0})
            symbol_history = symbol_history["history"]

            symbol_history_srz = SymbolHistorySerializer(symbol_history, many=True)

            set_json_cache(cache_key, symbol_history_srz.data, SIXTY_MINUTES_CACHE)
            return Response(symbol_history_srz.data, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
