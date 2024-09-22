from core.configs import SIXTY_SECONDS_CACHE
from core.utils import RedisInterface, set_json_cache, get_cache_as_json
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
class AssetOptionSymbolsAPIView(APIView):
    def post(self, request):
        asset_name = request.data.get("asset_name")
        cache_key = f"OPTIONS_ASSET_SYMBOLS_a_{asset_name}"
        cache_response = get_cache_as_json(cache_key)

        if cache_response is None:
            redis_conn = RedisInterface(db=3)
            calls_list = redis_conn.get_list_of_dicts(list_key="calls")
            puts_list = redis_conn.get_list_of_dicts(list_key="puts")
            calls_puts_list = calls_list + puts_list

            asset_options_list = []
            for option in calls_puts_list:
                if option["asset_name"] == asset_name:
                    asset_options_list.append(option["symbol"])

            asset_options_list = sorted(asset_options_list)
            set_json_cache(cache_key, asset_options_list, SIXTY_SECONDS_CACHE)
            return Response(asset_options_list, status=status.HTTP_200_OK)

        else:
            return Response(cache_response, status=status.HTTP_200_OK)
