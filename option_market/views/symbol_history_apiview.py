from core.configs import SIXTY_MINUTES_CACHE, OPTION_DB
from core.utils import MongodbInterface, set_json_cache, get_cache_as_json
from option_market.serializers import SymbolHistorySerializer
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
